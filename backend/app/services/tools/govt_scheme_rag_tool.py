import os
import time
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

try:
    from pinecone import Pinecone
    from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
    PINECONE_AVAILABLE = True
except ImportError:
    logger.warning("Pinecone or Google AI dependencies not available. RAG functionality will be limited.")
    PINECONE_AVAILABLE = False

# Keep in sync with build_kb.py
INDEX_NAME = "government-schemes-db"
EMBED_MODEL = "models/embedding-001"

# Global cached clients
_cached_index = None
_cached_embeddings = None
_cached_llm = None


def get_cached_clients() -> Tuple[Any, Any]:
    """Get cached Pinecone index and Google embeddings clients."""
    global _cached_index, _cached_embeddings
    
    if _cached_index is None or _cached_embeddings is None:
        api_key = settings.pinecone_api_key
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY not set in settings")

        google_api_key = settings.GOOGLE_API_KEY
        if not google_api_key:
            raise RuntimeError("GOOGLE_API_KEY not set in settings")
        
        os.environ["GOOGLE_API_KEY"] = google_api_key

        pc = Pinecone(api_key=api_key)
        _cached_index = pc.Index(INDEX_NAME)
        
        _cached_embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)
        logger.info("✅ Google embeddings and Pinecone clients cached successfully")
    
    return _cached_index, _cached_embeddings


def recommend(query: str, top_k: int = 30, top_n_schemes: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve matching govt schemes for a free-text query using Google embeddings.

    Returns a list of unique schemes with minimal info and why-match snippets.
    """
    if not query or not str(query).strip():
        return []

    # Use cached Google embeddings
    index, embeddings = get_cached_clients()
    
    # Get query embedding using Google API
    query_embedding = embeddings.embed_query(query)
    
    # Direct Pinecone query
    response = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        namespace="default"
    )
    
    # Convert Pinecone results to our format
    hits = []
    for match in response.matches:
        # Create a mock document object to match the original structure
        class MockDoc:
            def __init__(self, content, metadata):
                self.page_content = content
                self.metadata = metadata
        
        # Extract content from the 'text' field in metadata
        content = match.metadata.get('text', '') or ''
        
        doc = MockDoc(content, match.metadata)
        score = float(match.score)
        hits.append((doc, score))

    # Aggregate to unique schemes by first/highest-ranked hit
    by_scheme: Dict[str, Dict[str, Any]] = {}
    for doc, score in hits:
        sid = doc.metadata.get("scheme_id") or ""
        if not sid:
            continue
        if sid not in by_scheme:
            by_scheme[sid] = {
                "id": sid,
                "name": doc.metadata.get("scheme_name") or "",
                "url": doc.metadata.get("url") or "",
                "score": score,
                "sections": set(),
                "section_content": {},
                "why_match": [],
            }
        entry = by_scheme[sid]
        try:
            entry["score"] = max(entry["score"], score)
        except Exception:
            entry["score"] = score
        section = doc.metadata.get("section")
        if section:
            entry["sections"].add(section)
            # Store the full content for each section
            content = (doc.page_content or "").strip()
            if content:
                entry["section_content"][section] = content
        content = (doc.page_content or "").strip().replace("\n", " ")
        if content:
            entry["why_match"].append(content[:240])

    results = []
    for v in by_scheme.values():
        v["sections"] = sorted(list(v["sections"]))
        results.append(v)

    try:
        results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    except Exception:
        pass

    return results[:top_n_schemes]


def search_schemes(query: str, top_k: int = 30) -> List[Dict[str, Any]]:
    """Alias for recommend() keeping old naming neutral."""
    return recommend(query, top_k=top_k, top_n_schemes=top_k)


def get_cached_llm():
    """Get cached Gemini LLM for generation"""
    global _cached_llm
    
    if _cached_llm is None:
        google_api_key = settings.GOOGLE_API_KEY
        os.environ["GOOGLE_API_KEY"] = google_api_key
        _cached_llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,
            max_tokens=300
        )
        logger.info("✅ Gemini LLM client cached successfully")
    
    return _cached_llm


def generate_rag_response(query: str, retrieved_schemes: List[Dict], llm) -> str:
    """Generate natural language response using retrieved schemes"""
    
    # Build context from retrieved schemes
    context_parts = []
    for i, scheme in enumerate(retrieved_schemes[:3], 1):  # Top 3 schemes
        # Get first few items from why_match for context
        why_match = scheme.get('why_match', [])
        benefits_preview = why_match[0][:300] if why_match else "Information not available"
        
        context_parts.append(f"""
                                Scheme {i}: {scheme['name']}
                                URL: {scheme.get('url', 'N/A')}
                                Matching Sections: {', '.join(scheme.get('sections', []))}
                                Relevant Content: {benefits_preview}
                                Match Score: {scheme.get('score', 0):.3f}
                                """)
    
    context = "\n".join(context_parts)
    
    # Create prompt for Gemini
    prompt = f"""You are an expert agricultural advisor helping Indian farmers find suitable government schemes.

                User Query: "{query}"

                Based on the following relevant government schemes from my database:

                {context}

                Provide a SHORT response with ONLY these sections:

                **Recommended Schemes**: One line summary of the best scheme(s)
                **Key Benefits**: One line about main financial benefits/subsidies
                **Eligibility**: One line about who can apply
                **How to Apply**: One line about application process
                **Next Steps**: One line about immediate action to take

                Guidelines:
                - Keep each section to ONE LINE only
                - Use simple language
                - Be specific about subsidy amounts if mentioned
                - Maximum 5 lines total

                Response:"""

    try:
        # Generate response using Gemini
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        return f"I found {len(retrieved_schemes)} relevant schemes for your query, but I'm having trouble generating a detailed response right now. Please check the scheme details directly or contact your local agriculture office. Error: {str(e)}"


def recommend_with_rag(query: str, top_k: int = 30, top_n_schemes: int = 3) -> Dict:
    """Complete RAG pipeline: Retrieve + Generate"""
    
    # Step 1: Retrieve (existing function)
    retrieved_schemes = recommend(query, top_k, top_n_schemes)
    
    if not retrieved_schemes:
        return {
            "schemes": [],
            "rag_response": "I couldn't find any matching government schemes for your query. Please try rephrasing your question or contact your local agriculture office for assistance.",
            "query": query
        }
    
    # Step 2: Generate
    try:
        llm = get_cached_llm()
        rag_response = generate_rag_response(query, retrieved_schemes, llm)
    except Exception as e:
        rag_response = f"I found {len(retrieved_schemes)} relevant schemes, but I'm having trouble generating a detailed response. Please check the scheme details below. Error: {str(e)}"
    
    return {
        "schemes": retrieved_schemes,
        "rag_response": rag_response,
        "query": query
    }


class GovtSchemeRAGTool:
    
    def __init__(self):
        self.pinecone_available = PINECONE_AVAILABLE
        
        if not self.pinecone_available:
            logger.warning("Google AI or Pinecone not available, using fallback mock responses")
    
    async def search_schemes(self, query: str, top_k: int = 30, top_n_schemes: int = 3) -> Dict[str, Any]:
        logger.info("======== Government Schemes RAG Search ========")
        logger.info(f"Query: {query}")
        logger.info(f"Google AI available: {self.pinecone_available}")
        
        if not query or not str(query).strip():
            return {
                "success": False,
                "error": "Empty query provided",
                "schemes": [],
                "total_schemes": 0
            }
        
        try:
            start_time = time.time()
            
            if self.pinecone_available:
                # Use the updated RAG pipeline function
                rag_result = recommend_with_rag(query, top_k, top_n_schemes)
                schemes = rag_result["schemes"]
                rag_response = rag_result["rag_response"]
            else:
                schemes = self._fallback_search(query, top_n_schemes)
                rag_response = "RAG response generation is not available. Using fallback search results."
            
            end_time = time.time()
            response_time = end_time - start_time
            
            logger.info(f"RAG search completed in {response_time:.2f}s")
            logger.info(f"Found {len(schemes)} matching schemes")
            
            return {
                "success": True,
                "schemes": schemes,
                "rag_response": rag_response,
                "total_schemes": len(schemes),
                "query": query,
                "response_time": response_time,
                "using_rag": self.pinecone_available
            }
        
        except Exception as e:
            logger.error(f"Government Schemes RAG search failed: {str(e)}")
            
            # Fallback to mock results
            fallback_schemes = self._fallback_search(query, top_n_schemes)
            return {
                "success": True,
                "schemes": fallback_schemes,
                "rag_response": "I encountered an issue with the AI system, but I found some relevant schemes based on keyword matching. Please review the schemes below.",
                "total_schemes": len(fallback_schemes),
                "query": query,
                "error": f"RAG search failed, using fallback: {str(e)}",
                "using_rag": False
            }
    
    def _fallback_search(self, query: str, top_n: int) -> List[Dict[str, Any]]:
        logger.info("Using fallback mock scheme search")
        
        mock_schemes = [
            {
                "id": "pmksy-pdmc",
                "name": "Pradhan Mantri Krishi Sinchayee Yojana: Per Drop More Crop",
                "url": "https://www.myscheme.gov.in/schemes/pmksypdmc",
                "score": 0.85,
                "sections": ["details", "benefits", "eligibility"],
                "why_match": ["Micro irrigation and drip irrigation financial assistance for farmers"]
            },
            {
                "id": "pmfby",
                "name": "Pradhan Mantri Fasal Bima Yojana",
                "url": "https://www.pmfby.gov.in/",
                "score": 0.75,
                "sections": ["benefits", "eligibility"],
                "why_match": ["Crop insurance scheme providing financial support against crop loss"]
            },
            {
                "id": "pm-kisan",
                "name": "PM-KISAN Samman Nidhi",
                "url": "https://pmkisan.gov.in/",
                "score": 0.70,
                "sections": ["benefits", "application_process"],
                "why_match": ["₹6000 annual income support to small and marginal farmers"]
            },
            {
                "id": "kcc",
                "name": "Kisan Credit Card",
                "url": "https://www.nabard.org/content1.aspx?id=543",
                "score": 0.65,
                "sections": ["details", "eligibility", "documents_required"],
                "why_match": ["Credit facility for agriculture and allied activities"]
            }
        ]
        
        # Simple keyword-based filtering
        query_lower = query.lower()
        relevant_schemes = []
        
        for scheme in mock_schemes:
            scheme_text = f"{scheme['name']} {' '.join(scheme['why_match'])}".lower()
            
            # Check for keyword matches
            if any(word in scheme_text for word in query_lower.split()):
                relevant_schemes.append(scheme)
        
        # If no matches, return all schemes
        if not relevant_schemes:
            relevant_schemes = mock_schemes
        
        return relevant_schemes[:top_n]
    
    async def recommend_schemes(self, 
                               query: str, 
                               farmer_context: Optional[Dict[str, Any]] = None,
                               top_n: int = 3) -> Dict[str, Any]:
        logger.info("======== Government Schemes Recommendation ========")
        logger.info(f"Query: {query}")
        logger.info(f"Farmer context: {farmer_context}")
        
        # Enhanced query with farmer context
        enhanced_query = query
        if farmer_context:
            crops = farmer_context.get("crops", [])
            farmer_type = farmer_context.get("farmer_type", "")
            location = farmer_context.get("location", "")
            
            context_terms = []
            if crops:
                context_terms.extend(crops)
            if farmer_type:
                context_terms.append(farmer_type)
            if location:
                context_terms.append(location)
            
            if context_terms:
                enhanced_query = f"{query} {' '.join(context_terms)}"
        
        # Search for schemes using RAG
        search_result = await self.search_schemes(enhanced_query, top_n_schemes=top_n)
        
        if not search_result.get("success"):
            return search_result
        
        schemes = search_result.get("schemes", [])
        rag_response = search_result.get("rag_response", "")
        
        # Format response for recommendations
        recommendations = []
        for scheme in schemes:
            # Deduplicate why_match content
            why_match_items = scheme.get("why_match", [])
            unique_why_match = []
            seen = set()
            for item in why_match_items:
                if item not in seen:
                    unique_why_match.append(item)
                    seen.add(item)
            why_match_text = ". ".join(unique_why_match[:2])
            
            recommendation = {
                "scheme_name": scheme.get("name", ""),
                "scheme_url": scheme.get("url", ""),
                "relevance_score": scheme.get("score", 0.0),
                "matched_sections": scheme.get("sections", []),
                "why_relevant": why_match_text,
                "recommendation_text": self._generate_recommendation_text(scheme, farmer_context)
            }
            recommendations.append(recommendation)
        
        return {
            "success": True,
            "recommendations": recommendations,
            "rag_response": rag_response,
            "total_found": len(recommendations),
            "query": query,
            "enhanced_query": enhanced_query,
            "farmer_context": farmer_context,
            "using_rag": search_result.get("using_rag", False)
        }
    
    def _generate_recommendation_text(self, scheme: Dict[str, Any], context: Optional[Dict[str, Any]]) -> str:
        scheme_name = scheme.get("name", "")
        sections = scheme.get("sections", [])
        
        if "eligibility" in sections and "benefits" in sections:
            return f"You may be eligible for {scheme_name}. Check the eligibility criteria and apply for financial assistance."
        elif "benefits" in sections:
            return f"{scheme_name} provides financial benefits for farmers. Consider applying if eligible."
        else:
            return f"{scheme_name} is a relevant government scheme for your agricultural needs."
    
    async def get_scheme_details(self, scheme_id: str) -> Dict[str, Any]:
        logger.info(f"Getting details for scheme: {scheme_id}")
        
        return {
            "success": True,
            "scheme_id": scheme_id,
            "message": "Detailed scheme information would be retrieved from Pinecone vector database",
            "note": "This endpoint can be enhanced to fetch comprehensive scheme details"
        }
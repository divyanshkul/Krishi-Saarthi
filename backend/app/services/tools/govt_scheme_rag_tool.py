import os
import time
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

try:
    from pinecone import Pinecone
    from langchain_huggingface import HuggingFaceEmbeddings
    PINECONE_AVAILABLE = True
except ImportError:
    logger.warning("Pinecone dependencies not available. RAG functionality will be limited.")
    PINECONE_AVAILABLE = False


# Keep in sync with build_kb.py
INDEX_NAME = "government-schemes"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def init_clients() -> Tuple[Any, Any]:
    """Initialize Pinecone index client and embeddings."""
    api_key = settings.pinecone_api_key
    if not api_key:
        raise RuntimeError("PINECONE_API_KEY not set in settings")

    pc = Pinecone(api_key=api_key)
    index = pc.Index(INDEX_NAME)
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return index, embeddings


def recommend(query: str, top_k: int = 30, top_n_schemes: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve matching govt schemes for a free-text query.

    Returns a list of unique schemes with minimal info and why-match snippets.
    """
    if not query or not str(query).strip():
        return []

    # Use direct Pinecone queries instead of LangChain wrapper
    index, embeddings = init_clients()
    
    # Get query embedding
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


class GovtSchemeRAGTool:
    
    def __init__(self):
        self.pinecone_available = PINECONE_AVAILABLE
        
        if not self.pinecone_available:
            logger.warning("Pinecone not available, using fallback mock responses")
    
    async def search_schemes(self, query: str, top_k: int = 30, top_n_schemes: int = 3) -> Dict[str, Any]:
        logger.info("======== Government Schemes RAG Search ========")
        logger.info(f"Query: {query}")
        logger.info(f"Pinecone available: {self.pinecone_available}")
        
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
                # Use the original RAG pipeline function
                schemes = recommend(query, top_k, top_n_schemes)
            else:
                schemes = self._fallback_search(query, top_n_schemes)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            logger.info(f"RAG search completed in {response_time:.2f}s")
            logger.info(f"Found {len(schemes)} matching schemes")
            
            return {
                "success": True,
                "schemes": schemes,
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
        
        # Search for schemes
        search_result = await self.search_schemes(enhanced_query, top_n_schemes=top_n)
        
        if not search_result.get("success"):
            return search_result
        
        schemes = search_result.get("schemes", [])
        
        # Format response for recommendations
        recommendations = []
        for scheme in schemes:
            why_match_text = ". ".join(scheme.get("why_match", [])[:2])
            
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
        
        # For now, return basic info - could be enhanced with more detailed Pinecone queries
        return {
            "success": True,
            "scheme_id": scheme_id,
            "message": "Detailed scheme information would be retrieved from Pinecone vector database",
            "note": "This endpoint can be enhanced to fetch comprehensive scheme details"
        }
from typing import Dict, Any, List
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GovtSchemeTool:
    """
    Government Scheme Tool - Rule-based scheme matching
    Matches farmers to relevant government schemes and subsidies
    """
    
    def __init__(self):
        # Mock scheme database - in production, this would be a proper database or API
        self.schemes = [
            {
                "name": "PM-KISAN Samman Nidhi",
                "description": "₹6000 annual income support to farmer families",
                "eligibility": ["small farmers", "marginal farmers", "landholders"],
                "documents": ["Aadhaar", "bank account", "land records"],
                "keywords": ["income support", "direct benefit", "financial help"]
            },
            {
                "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                "description": "Crop insurance scheme providing financial support against crop loss",
                "eligibility": ["all farmers", "tenant farmers", "sharecroppers"],
                "documents": ["Aadhaar", "bank account", "land ownership proof", "crop details"],
                "keywords": ["crop insurance", "loss protection", "weather damage", "natural calamity"]
            },
            {
                "name": "Kisan Credit Card (KCC)",
                "description": "Credit facility for agriculture and allied activities",
                "eligibility": ["farmers", "self help groups", "joint liability groups"],
                "documents": ["Aadhaar", "PAN", "land documents", "income proof"],
                "keywords": ["credit", "loan", "financing", "agriculture loan"]
            },
            {
                "name": "Soil Health Card Scheme",
                "description": "Free soil testing and nutrient recommendations",
                "eligibility": ["all farmers"],
                "documents": ["land records", "farmer registration"],
                "keywords": ["soil testing", "nutrients", "soil health", "fertilizer recommendation"]
            },
            {
                "name": "National Agriculture Market (e-NAM)",
                "description": "Online trading platform for agricultural commodities",
                "eligibility": ["farmers", "traders", "commission agents"],
                "documents": ["registration", "trade license"],
                "keywords": ["market", "selling", "trade", "price discovery", "online market"]
            }
        ]
    
    async def find_schemes(self, 
                          query: str, 
                          farmer_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Find relevant government schemes based on farmer query and context
        """
        logger.info(f"Government Scheme Tool processing: {query[:50]}...")
        
        try:
            # Match schemes based on query keywords
            relevant_schemes = self._match_schemes(query)
            
            if not relevant_schemes:
                relevant_schemes = [self.schemes[0]]  # Default to PM-KISAN
            
            # Format response
            response_text = self._format_scheme_response(relevant_schemes)
            
            return {
                "success": True,
                "response": response_text,
                "schemes_found": len(relevant_schemes),
                "scheme_names": [scheme["name"] for scheme in relevant_schemes],
                "source": "government_schemes_db",
                "query": query
            }
        
        except Exception as e:
            logger.error(f"Government Scheme Tool failed: {str(e)}")
            return {
                "success": False,
                "error": f"Scheme matching error: {str(e)}",
                "source": "government_schemes_db"
            }
    
    def _match_schemes(self, query: str) -> List[Dict[str, Any]]:
        """Match schemes based on query keywords"""
        query_lower = query.lower()
        matched_schemes = []
        
        for scheme in self.schemes:
            # Check if any scheme keywords match the query
            scheme_keywords = scheme.get("keywords", [])
            if any(keyword in query_lower for keyword in scheme_keywords):
                matched_schemes.append(scheme)
        
        # If no specific matches, check for general financial terms
        if not matched_schemes:
            financial_terms = ["help", "support", "subsidy", "loan", "money", "assistance", "scheme"]
            if any(term in query_lower for term in financial_terms):
                matched_schemes.append(self.schemes[0])  # PM-KISAN as default
        
        return matched_schemes
    
    def _format_scheme_response(self, schemes: List[Dict[str, Any]]) -> str:
        """Format schemes into a readable response"""
        if len(schemes) == 1:
            scheme = schemes[0]
            documents = ", ".join(scheme["documents"])
            return f"You may be eligible for {scheme['name']}. {scheme['description']} Required documents: {documents}. Visit your nearest CSC or agriculture office for enrollment."
        
        elif len(schemes) > 1:
            scheme_names = [scheme["name"] for scheme in schemes[:2]]  # Show top 2
            return f"You may be eligible for multiple schemes including {' and '.join(scheme_names)}. Visit your nearest agriculture office with Aadhaar and land documents for detailed information and enrollment assistance."
        
        else:
            return "Visit your nearest agriculture office to explore available government schemes and subsidies based on your specific farming situation."
from typing import Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)


class KCCTool:
    """
    Kisan Call Center Tool - Mock implementation
    Future: Will connect to GPU server with fine-tuned KCC model
    """
    
    def __init__(self):
        self.mock_responses = [
            "Based on traditional farming knowledge, ensure proper soil preparation and follow seasonal planting guidelines for optimal yield.",
            "Regular monitoring of crop health and timely application of organic fertilizers can significantly improve your harvest quality.",
            "Consider crop rotation practices and maintain adequate spacing between plants for better growth and disease prevention.",
            "Proper irrigation scheduling based on crop growth stages and local weather conditions is essential for successful farming.",
            "Integrated pest management using both biological and chemical methods provides the best protection for your crops."
        ]
    
    async def get_advice(self, query: str) -> Dict[str, Any]:
        """
        Get farming advice based on query
        Currently returns mock responses, will be replaced with GPU server API call
        """
        logger.info(f"KCC Tool processing query: {query[:50]}...")
        
        try:
            # Mock response selection based on query content
            response_text = self._select_mock_response(query)
            
            return {
                "success": True,
                "response": response_text,
                "source": "kcc_knowledge_base",
                "confidence": 0.7,
                "query": query
            }
        
        except Exception as e:
            logger.error(f"KCC Tool failed: {str(e)}")
            return {
                "success": False,
                "error": f"KCC knowledge base error: {str(e)}",
                "source": "kcc_knowledge_base"
            }
    
    def _select_mock_response(self, query: str) -> str:
        """Select appropriate mock response based on query keywords"""
        query_lower = query.lower()
        
        # Simple keyword-based response selection
        if any(word in query_lower for word in ["soil", "prepare", "planting"]):
            return "Ensure proper soil preparation by testing pH levels and adding organic matter. Follow recommended spacing and planting depth for your specific crop variety."
        
        elif any(word in query_lower for word in ["fertilizer", "nutrients", "growth"]):
            return "Apply balanced NPK fertilizers based on soil test results. Supplement with organic compost and ensure adequate micronutrient availability for healthy plant growth."
        
        elif any(word in query_lower for word in ["irrigation", "water", "watering"]):
            return "Maintain consistent soil moisture without waterlogging. Use drip irrigation where possible and water during early morning or evening to reduce evaporation losses."
        
        elif any(word in query_lower for word in ["pest", "disease", "protection"]):
            return "Implement integrated pest management combining cultural, biological, and chemical controls. Regular field monitoring helps in early detection and timely intervention."
        
        else:
            # Default general advice
            import random
            return random.choice(self.mock_responses)
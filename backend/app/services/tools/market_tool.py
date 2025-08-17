from typing import Dict, Any
import random
from datetime import datetime, timedelta
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MarketTool:
    """
    Market Price Tool - Mock implementation for mandi prices and market intelligence
    Future: Will integrate with data.gov.in APIs and price forecasting models
    """
    
    def __init__(self):
        # Mock price data - in production, this would come from APIs
        self.mock_prices = {
            "wheat": {"price": 2150, "unit": "quintal", "trend": "stable", "change": 2.3},
            "rice": {"price": 2800, "unit": "quintal", "trend": "up", "change": 5.1},
            "tomato": {"price": 45, "unit": "kg", "trend": "down", "change": -8.2},
            "onion": {"price": 35, "unit": "kg", "trend": "up", "change": 12.5},
            "potato": {"price": 28, "unit": "kg", "trend": "stable", "change": 1.8},
            "cotton": {"price": 6200, "unit": "quintal", "trend": "up", "change": 3.7},
            "sugarcane": {"price": 350, "unit": "quintal", "trend": "stable", "change": 0.5}
        }
        
        self.market_locations = [
            "Local Mandi", "District Market", "APMC Market", "Nearby Agricultural Market"
        ]
    
    async def get_market_info(self, 
                            query: str, 
                            crop: str = None, 
                            location: str = None) -> Dict[str, Any]:
        """
        Get market price information and selling recommendations
        """
        logger.info(f"Market Tool processing: {query[:50]}...")
        
        try:
            # Extract crop from query if not provided
            if not crop:
                crop = self._extract_crop_from_query(query)
            
            # Get price information
            price_info = self._get_price_info(crop)
            
            # Generate market advice
            market_advice = self._generate_market_advice(crop, price_info)
            
            # Format response
            response_text = self._format_market_response(crop, price_info, market_advice)
            
            return {
                "success": True,
                "response": response_text,
                "crop": crop,
                "current_price": price_info.get("price"),
                "trend": price_info.get("trend"),
                "source": "market_intelligence",
                "query": query
            }
        
        except Exception as e:
            logger.error(f"Market Tool failed: {str(e)}")
            return {
                "success": False,
                "error": f"Market data error: {str(e)}",
                "source": "market_intelligence"
            }
    
    def _extract_crop_from_query(self, query: str) -> str:
        """Extract crop name from query"""
        query_lower = query.lower()
        
        # Check for crop names in the query
        for crop in self.mock_prices.keys():
            if crop in query_lower:
                return crop
        
        # Check for common crop aliases
        crop_aliases = {
            "paddy": "rice",
            "bajra": "wheat",
            "maize": "wheat",
            "corn": "wheat"
        }
        
        for alias, crop in crop_aliases.items():
            if alias in query_lower:
                return crop
        
        # Default to wheat if no specific crop found
        return "wheat"
    
    def _get_price_info(self, crop: str) -> Dict[str, Any]:
        """Get current price information for crop"""
        if crop in self.mock_prices:
            base_info = self.mock_prices[crop].copy()
            
            # Add some realistic variation to mock data
            price_variation = random.uniform(-50, 50)
            base_info["price"] += int(price_variation)
            
            # Add market location
            base_info["market"] = random.choice(self.market_locations)
            
            # Add date
            base_info["date"] = datetime.now().strftime("%Y-%m-%d")
            
            return base_info
        else:
            # Default price info
            return {
                "price": random.randint(2000, 3000),
                "unit": "quintal",
                "trend": random.choice(["up", "down", "stable"]),
                "change": random.uniform(-10, 10),
                "market": random.choice(self.market_locations),
                "date": datetime.now().strftime("%Y-%m-%d")
            }
    
    def _generate_market_advice(self, crop: str, price_info: Dict[str, Any]) -> str:
        """Generate market advice based on price trends"""
        trend = price_info.get("trend", "stable")
        change = price_info.get("change", 0)
        
        if trend == "up" and change > 5:
            return "Prices are rising strongly. Good time to sell if you have ready produce."
        elif trend == "up":
            return "Prices are showing upward trend. Consider selling in the next few days."
        elif trend == "down" and change < -5:
            return "Prices are declining. If possible, hold your produce for a few days to see market recovery."
        elif trend == "down":
            return "Prices are slightly down. Monitor for 2-3 days before deciding to sell."
        else:
            return "Prices are stable. You can sell at current rates or wait for seasonal demand increase."
    
    def _format_market_response(self, 
                               crop: str, 
                               price_info: Dict[str, Any], 
                               advice: str) -> str:
        """Format market information into readable response"""
        price = price_info.get("price", 0)
        unit = price_info.get("unit", "quintal")
        trend = price_info.get("trend", "stable")
        change = price_info.get("change", 0)
        market = price_info.get("market", "Local Market")
        
        change_text = f"up {change:.1f}%" if change > 0 else f"down {abs(change):.1f}%" if change < 0 else "stable"
        
        return f"Current {crop} price: ₹{price}/{unit} at {market} ({change_text} from last week). {advice} Check multiple mandis for best rates."
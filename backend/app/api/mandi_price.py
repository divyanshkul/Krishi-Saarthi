from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import time

from app.services.tools.lstm_price_tool import LSTMPriceTool
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/mandi-price", tags=["Mandi Price Prediction"])

lstm_tool = LSTMPriceTool()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Mandi Price Prediction API",
        "timestamp": time.time(),
        "lstm_available": lstm_tool.pytorch_available,
        "supported_crops": lstm_tool.supported_crops
    }


@router.post("/predict/weekly")
async def predict_weekly_prices(request: Dict[str, Any]):
    logger.info("======== Weekly Price Prediction API ========")
    
    try:
        crop = request.get("crop", "").strip().lower()
        if not crop:
            raise HTTPException(status_code=400, detail="Crop parameter is required")
        
        location = request.get("location", None)
        
        logger.info(f"Crop: {crop}")
        logger.info(f"Location: {location}")
        
        result = await lstm_tool.predict_weekly_prices(
            crop=crop,
            location=location
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Weekly price prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/analyze")
async def analyze_market_trends(request: Dict[str, Any]):
    logger.info("======== Market Analysis API ========")
    
    try:
        crop = request.get("crop", "").strip().lower()
        if not crop:
            raise HTTPException(status_code=400, detail="Crop parameter is required")
        
        logger.info(f"Analyzing market trends for: {crop}")
        
        result = await lstm_tool.analyze_market_trends(crop=crop)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Market analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/examples")
async def get_example_requests():
    return {
        "predict_weekly_example": {
            "url": "POST /api/mandi-price/predict/weekly",
            "request_body": {
                "crop": "rice",
                "location": "Punjab"
            },
            "description": "Get 7-day price predictions for a specific crop"
        },
        "analyze_example": {
            "url": "POST /api/mandi-price/analyze",
            "request_body": {
                "crop": "ajwan"
            },
            "description": "Get comprehensive market analysis including trends and trading recommendations"
        },
        "supported_crops": {
            "url": "GET /api/mandi-price/crops",
            "description": "Get list of supported crops for prediction"
        },
        "available_crops": ["rice", "ajwan", "sugarcane"],
        "sample_response": {
            "success": True,
            "crop": "rice",
            "predictions": [
                {
                    "day": 1,
                    "date": "2025-08-19",
                    "weekday": "Tuesday",
                    "min_price": 7159.56,
                    "max_price": 10811.64,
                    "modal_price": 9804.17,
                    "price_range": 3652.08
                }
            ],
            "analysis": {
                "price_summary": {
                    "average_modal": 9500.50,
                    "lowest_price": 8980.93,
                    "highest_price": 9804.17
                },
                "trend_analysis": {
                    "trend": "Falling",
                    "net_change": -823.24,
                    "change_percent": -8.4
                },
                "trading_recommendations": {
                    "best_buy_day": "Monday",
                    "best_sell_day": "Tuesday",
                    "potential_profit": 823.24
                }
            }
        }
    }
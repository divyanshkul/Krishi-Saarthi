import os
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import warnings

from app.utils.logger import get_logger

# Suppress sklearn warnings about feature names
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

logger = get_logger(__name__)

try:
    import torch
    import torch.nn as nn
    import numpy as np
    import joblib
    PYTORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch dependencies not available. LSTM functionality will be limited.")
    PYTORCH_AVAILABLE = False

# Global cached models
_cached_models = {}


class PriceLSTM(nn.Module):
    def __init__(self, input_size=3, hidden_size=50, num_layers=2, output_size=3):
        super(PriceLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=0.2 if num_layers > 1 else 0)
        self.fc1 = nn.Linear(hidden_size, 25)
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(25, output_size)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = out[:, -1, :]
        out = self.fc1(out)
        out = self.dropout(out)
        out = self.fc2(out)
        return out


def get_cached_model(crop: str) -> tuple:
    """Get cached model, scaler, and data for the specified crop."""
    global _cached_models
    
    if crop not in _cached_models:
        logger.info(f"Loading LSTM model for {crop}...")
        
        # Get model path
        base_path = Path(__file__).parent.parent.parent / "models" / "lstm" / crop
        model_path = base_path / f"mandi_lstm_{crop}_model.pth"
        scaler_path = base_path / f"price_scaler_{crop}.pkl"
        data_path = base_path / f"scaled_prices_{crop}.npy"
        
        if not all(path.exists() for path in [model_path, scaler_path, data_path]):
            raise FileNotFoundError(f"Missing model files for crop: {crop}")
        
        # Set device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load model
        model = PriceLSTM()
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)
        model.eval()
        
        # Load scaler
        scaler = joblib.load(scaler_path)
        
        # Load scaled prices
        scaled_prices = np.load(data_path)
        
        _cached_models[crop] = {
            'model': model,
            'scaler': scaler,
            'scaled_prices': scaled_prices,
            'device': device
        }
        
        logger.info(f"✅ LSTM model for {crop} cached successfully")
    
    return (
        _cached_models[crop]['model'],
        _cached_models[crop]['scaler'],
        _cached_models[crop]['scaled_prices'],
        _cached_models[crop]['device']
    )


def predict_7_days(crop: str) -> List[Dict[str, Any]]:
    """Generate 7-day price predictions for the specified crop."""
    model, scaler, scaled_prices, device = get_cached_model(crop)
    
    predictions = []
    current_sequence = scaled_prices[-30:].copy()
    today = datetime.now()
    
    for day in range(7):
        # Make prediction
        with torch.no_grad():
            input_tensor = torch.FloatTensor(current_sequence).unsqueeze(0).to(device)
            prediction = model(input_tensor)
            pred_scaled = prediction.cpu().numpy()
            pred_prices = scaler.inverse_transform(pred_scaled)[0]
        
        # Format prediction
        prediction_date = today + timedelta(days=day + 1)
        day_pred = {
            'day': day + 1,
            'date': prediction_date.strftime('%Y-%m-%d'),
            'weekday': prediction_date.strftime('%A'),
            'min_price': float(round(pred_prices[0], 2)),
            'max_price': float(round(pred_prices[1], 2)),
            'modal_price': float(round(pred_prices[2], 2)),
            'price_range': float(round(pred_prices[1] - pred_prices[0], 2))
        }
        predictions.append(day_pred)
        
        # Update sequence for next prediction
        next_pred_scaled = scaler.transform([pred_prices])[0]
        current_sequence = np.vstack([current_sequence[1:], next_pred_scaled])
    
    return predictions


def analyze_predictions(predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze and summarize price predictions."""
    modal_prices = [p['modal_price'] for p in predictions]
    avg_modal = float(np.mean(modal_prices))
    min_modal = float(min(modal_prices))
    max_modal = float(max(modal_prices))
    
    # Price trend analysis
    day1_price = float(predictions[0]['modal_price'])
    day7_price = float(predictions[6]['modal_price'])
    price_change = float(day7_price - day1_price)
    price_change_pct = float((price_change / day1_price) * 100)
    
    if price_change > 50:
        trend = "Strong Rising"
        trend_emoji = "📈"
    elif price_change > 10:
        trend = "Rising"
        trend_emoji = "📈"
    elif price_change < -50:
        trend = "Strong Falling"
        trend_emoji = "📉"
    elif price_change < -10:
        trend = "Falling"
        trend_emoji = "📉"
    else:
        trend = "Stable"
        trend_emoji = "➡️"
    
    # Best trading days
    best_buy_day = min(predictions, key=lambda x: x['modal_price'])
    best_sell_day = max(predictions, key=lambda x: x['modal_price'])
    potential_profit = float(best_sell_day['modal_price'] - best_buy_day['modal_price'])
    
    # Volatility analysis
    volatility = float(np.std(modal_prices))
    if volatility > 200:
        volatility_level = "High"
    elif volatility < 50:
        volatility_level = "Low"
    else:
        volatility_level = "Moderate"
    
    return {
        "price_summary": {
            "average_modal": float(round(avg_modal, 2)),
            "lowest_price": float(min_modal),
            "highest_price": float(max_modal),
            "lowest_day": int(predictions[modal_prices.index(min_modal)]['day']),
            "highest_day": int(predictions[modal_prices.index(max_modal)]['day'])
        },
        "trend_analysis": {
            "week_start": float(day1_price),
            "week_end": float(day7_price),
            "trend": trend,
            "trend_emoji": trend_emoji,
            "net_change": float(round(price_change, 2)),
            "change_percent": float(round(price_change_pct, 1))
        },
        "trading_recommendations": {
            "best_buy_day": str(best_buy_day['weekday']),
            "best_buy_day_number": int(best_buy_day['day']),
            "best_buy_price": float(best_buy_day['modal_price']),
            "best_sell_day": str(best_sell_day['weekday']),
            "best_sell_day_number": int(best_sell_day['day']),
            "best_sell_price": float(best_sell_day['modal_price']),
            "potential_profit": float(round(potential_profit, 2)) if potential_profit > 0 else 0.0
        },
        "volatility": {
            "value": float(round(volatility, 2)),
            "level": volatility_level
        }
    }


class LSTMPriceTool:
    
    def __init__(self):
        self.pytorch_available = PYTORCH_AVAILABLE
        self.supported_crops = ["rice", "ajwan", "sugarcane"]
        
        if not self.pytorch_available:
            logger.warning("PyTorch not available, using fallback mock responses")
    
    async def predict_weekly_prices(self, crop: str, location: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"======== Weekly Price Prediction for {crop} ========")
        logger.info(f"Location: {location or 'General'}")
        
        if crop not in self.supported_crops:
            return {
                "success": False,
                "error": f"Unsupported crop: {crop}. Supported crops: {', '.join(self.supported_crops)}",
                "crop": crop
            }
        
        try:
            start_time = time.time()
            
            if self.pytorch_available:
                predictions = predict_7_days(crop)
            else:
                predictions = self._fallback_predictions(crop)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            logger.info(f"Price prediction completed in {response_time:.2f}s")
            logger.info(f"Generated {len(predictions)} daily predictions")
            
            return {
                "success": True,
                "crop": crop,
                "location": location,
                "predictions": predictions,
                "total_days": len(predictions),
                "response_time": response_time,
                "using_lstm": self.pytorch_available
            }
        
        except Exception as e:
            logger.error(f"Weekly price prediction failed: {str(e)}")
            
            # Fallback to mock predictions
            fallback_predictions = self._fallback_predictions(crop)
            return {
                "success": True,
                "crop": crop,
                "location": location,
                "predictions": fallback_predictions,
                "total_days": len(fallback_predictions),
                "error": f"LSTM prediction failed, using fallback: {str(e)}",
                "using_lstm": False
            }
    
    async def analyze_market_trends(self, crop: str) -> Dict[str, Any]:
        logger.info(f"======== Market Analysis for {crop} ========")
        
        try:
            # Get predictions first
            prediction_result = await self.predict_weekly_prices(crop)
            
            if not prediction_result.get("success"):
                return prediction_result
            
            predictions = prediction_result.get("predictions", [])
            if not predictions:
                return {
                    "success": False,
                    "error": "No predictions available for analysis",
                    "crop": crop
                }
            
            # Generate analysis
            if self.pytorch_available:
                analysis = analyze_predictions(predictions)
            else:
                analysis = self._fallback_analysis(predictions)
            
            return {
                "success": True,
                "crop": crop,
                "predictions": predictions,
                "analysis": analysis,
                "using_lstm": prediction_result.get("using_lstm", False)
            }
        
        except Exception as e:
            logger.error(f"Market analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"Market analysis failed: {str(e)}",
                "crop": crop
            }
    
    def _fallback_predictions(self, crop: str) -> List[Dict[str, Any]]:
        logger.info(f"Using fallback mock predictions for {crop}")
        
        # Mock price ranges based on crop
        price_ranges = {
            "rice": {"min": 6000, "max": 11000, "modal": 8500},
            "ajwan": {"min": 5000, "max": 9000, "modal": 7000},
            "sugarcane": {"min": 3000, "max": 5000, "modal": 4000}
        }
        
        base_prices = price_ranges.get(crop, {"min": 5000, "max": 8000, "modal": 6500})
        predictions = []
        today = datetime.now()
        
        for day in range(7):
            # Add some variation
            variation = (day - 3) * 50  # Slight trend
            prediction_date = today + timedelta(days=day + 1)
            
            min_price = base_prices["min"] + variation
            max_price = base_prices["max"] + variation
            modal_price = base_prices["modal"] + variation
            
            predictions.append({
                'day': day + 1,
                'date': prediction_date.strftime('%Y-%m-%d'),
                'weekday': prediction_date.strftime('%A'),
                'min_price': round(min_price, 2),
                'max_price': round(max_price, 2),
                'modal_price': round(modal_price, 2),
                'price_range': round(max_price - min_price, 2)
            })
        
        return predictions
    
    def _fallback_analysis(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Simple fallback analysis
        modal_prices = [p['modal_price'] for p in predictions]
        
        return {
            "price_summary": {
                "average_modal": round(np.mean(modal_prices), 2),
                "lowest_price": min(modal_prices),
                "highest_price": max(modal_prices),
                "lowest_day": 1,
                "highest_day": 7
            },
            "trend_analysis": {
                "week_start": predictions[0]['modal_price'],
                "week_end": predictions[6]['modal_price'],
                "trend": "Stable",
                "trend_emoji": "➡️",
                "net_change": 0,
                "change_percent": 0
            },
            "trading_recommendations": {
                "best_buy_day": "Monday",
                "best_buy_day_number": 1,
                "best_buy_price": min(modal_prices),
                "best_sell_day": "Sunday",
                "best_sell_day_number": 7,
                "best_sell_price": max(modal_prices),
                "potential_profit": round(max(modal_prices) - min(modal_prices), 2)
            },
            "volatility": {
                "value": round(np.std(modal_prices), 2),
                "level": "Low"
            }
        }
    
    async def get_supported_crops(self) -> Dict[str, Any]:
        return {
            "success": True,
            "supported_crops": self.supported_crops,
            "lstm_available": self.pytorch_available
        }
import httpx
from typing import Dict, Any
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class KCCTool:
    """
    Kisan Call Center Tool - API client for GPU server KCC service
    Specializes in crop variety recommendations and farming advice
    """
    
    def __init__(self):
        self.gpu_server_url = settings.gpu_server_base_url
        self.kcc_endpoint = settings.kcc_api_endpoint
        self.timeout = settings.gpu_timeout_seconds
        self.full_api_url = f"{self.gpu_server_url.rstrip('/')}{self.kcc_endpoint}"
    
    async def get_advice(self, query: str) -> Dict[str, Any]:
        """
        Get crop variety advice from GPU server KCC API
        """
        logger.info(f"KCC Tool processing query: {query[:50]}...")
        
        try:
            # Prepare form data payload
            form_data = {"query": query}
            
            # Make API call to GPU server with form-urlencoded
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Calling KCC API: {self.full_api_url}")
                response = await client.post(
                    self.full_api_url,
                    data=form_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                logger.info(f"KCC API response received: {result.get('success', False)}")
                
                # Handle the exact response structure from your API
                if result.get("success"):
                    return {
                        "success": True,
                        "response": result.get("response", "No response from KCC service"),
                        "source": "kcc_gpu_server",
                        "query": result.get("query", query),
                        "error": result.get("error")
                    }
                else:
                    return {
                        "success": False,
                        "response": result.get("response", ""),
                        "error": result.get("error", "Unknown error from KCC service"),
                        "source": "kcc_gpu_server",
                        "query": result.get("query", query)
                    }
        
        except httpx.RequestError as e:
            logger.error(f"KCC API request failed: {type(e).__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"KCC API connection error: {type(e).__name__}: {str(e)}",
                "source": "kcc_gpu_server"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"KCC API HTTP error: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"KCC API HTTP error: {e.response.status_code} - {e.response.text[:100]}",
                "source": "kcc_gpu_server"
            }
        except Exception as e:
            logger.error(f"KCC Tool unexpected error: {type(e).__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"KCC service error: {type(e).__name__}: {str(e)}",
                "source": "kcc_gpu_server"
            }

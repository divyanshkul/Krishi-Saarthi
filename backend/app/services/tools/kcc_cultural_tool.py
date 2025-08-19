import httpx
from typing import Dict, Any
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class KCCCulturalTool:
    """
    KCC Cultural Practices Tool - API client for GPU server KCC cultural practices service
    Specializes in farming practices like seed rates, spacing, fertilizers, irrigation
    """
    
    def __init__(self):
        self.gpu_server_url = settings.gpu_server_base_url
        self.cultural_endpoint = settings.kcc_cultural_endpoint
        self.timeout = settings.gpu_timeout_seconds
        self.full_api_url = f"{self.gpu_server_url.rstrip('/')}{self.cultural_endpoint}"
    
    async def get_practices(self, query: str) -> Dict[str, Any]:
        """
        Get cultural practices advice from GPU server KCC Cultural API
        """
        logger.info(f"KCC Cultural Tool processing query: {query[:50]}...")
        
        try:
            # Prepare form data payload
            form_data = {"query": query}
            
            # Make API call to GPU server with form-urlencoded
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Calling KCC Cultural API: {self.full_api_url}")
                response = await client.post(
                    self.full_api_url,
                    data=form_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                logger.info(f"KCC Cultural API response received: {result.get('success', False)}")
                
                # Handle the exact response structure from your API
                if result.get("success"):
                    return {
                        "success": True,
                        "response": result.get("response", "No response from KCC cultural service"),
                        "source": "kcc_cultural_gpu_server",
                        "query": result.get("query", query),
                        "error": result.get("error")
                    }
                else:
                    return {
                        "success": False,
                        "response": result.get("response", ""),
                        "error": result.get("error", "Unknown error from KCC cultural service"),
                        "source": "kcc_cultural_gpu_server",
                        "query": result.get("query", query)
                    }
        
        except httpx.RequestError as e:
            logger.error(f"KCC Cultural API request failed: {type(e).__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"KCC Cultural API connection error: {type(e).__name__}: {str(e)}",
                "source": "kcc_cultural_gpu_server"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"KCC Cultural API HTTP error: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"KCC Cultural API HTTP error: {e.response.status_code} - {e.response.text[:100]}",
                "source": "kcc_cultural_gpu_server"
            }
        except Exception as e:
            logger.error(f"KCC Cultural Tool unexpected error: {type(e).__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"KCC cultural service error: {type(e).__name__}: {str(e)}",
                "source": "kcc_cultural_gpu_server"
            }
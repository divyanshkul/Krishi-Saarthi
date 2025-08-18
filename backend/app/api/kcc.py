from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.tools.kcc_tool import KCCTool
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

kcc_tool = KCCTool()


@router.post("/query")
async def kcc_query(request: Dict[str, str]) -> Dict[str, Any]:
    """
    KCC (Kisan Call Center) Query Endpoint
    Processes crop variety and farming advice queries through GPU server
    """
    try:
        query = request.get("query", "").strip()
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        logger.info(f"KCC endpoint received query: {query[:50]}...")
        
        # Call KCC tool to process query via GPU server
        result = await kcc_tool.get_advice(query)
        
        if result.get("success"):
            logger.info("KCC query processed successfully")
            return {
                "success": True,
                "query": result.get("query", query),
                "response": result.get("response"),
                "error": result.get("error")
            }
        else:
            logger.error(f"KCC tool failed: {result.get('error')}")
            return {
                "success": False,
                "query": result.get("query", query),
                "response": result.get("response", ""),
                "error": result.get("error", "KCC service unavailable")
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"KCC endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def kcc_health() -> Dict[str, Any]:
    """
    Health check for KCC service
    """
    return {
        "service": "KCC (Kisan Call Center)",
        "status": "healthy",
        "gpu_server_url": kcc_tool.full_api_url,
        "description": "Crop variety recommendations and farming advice"
    }
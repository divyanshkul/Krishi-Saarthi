from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
import time

from app.services.tools.govt_scheme_rag_tool import GovtSchemeRAGTool
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/schemes", tags=["Government Schemes"])

rag_tool = GovtSchemeRAGTool()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Government Schemes RAG API",
        "timestamp": time.time(),
        "rag_available": rag_tool.pinecone_available
    }


@router.post("/search")
async def search_schemes(request: Dict[str, Any]):
    logger.info("======== Schemes Search API ========")
    
    try:
        query = request.get("query", "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        top_k = request.get("top_k", 30)
        top_n_schemes = request.get("top_n_schemes", 3)
        
        logger.info(f"Query: {query}")
        logger.info(f"Parameters: top_k={top_k}, top_n_schemes={top_n_schemes}")
        
        result = await rag_tool.search_schemes(
            query=query,
            top_k=top_k,
            top_n_schemes=top_n_schemes
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Schemes search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/recommend")
async def recommend_schemes(request: Dict[str, Any]):
    logger.info("======== Schemes Recommendation API ========")
    
    try:
        query = request.get("query", "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        farmer_context = request.get("farmer_context", None)
        top_n = request.get("top_n", 3)
        
        logger.info(f"Query: {query}")
        logger.info(f"Farmer context: {farmer_context}")
        
        result = await rag_tool.recommend_schemes(
            query=query,
            farmer_context=farmer_context,
            top_n=top_n
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Schemes recommendation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@router.get("/scheme/{scheme_id}")
async def get_scheme_details(scheme_id: str):
    logger.info(f"======== Get Scheme Details: {scheme_id} ========")
    
    try:
        result = await rag_tool.get_scheme_details(scheme_id)
        return result
    
    except Exception as e:
        logger.error(f"Failed to get scheme details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get details: {str(e)}")


@router.get("/test")
async def test_rag():
    logger.info("======== RAG Test Endpoint ========")
    
    try:
        test_query = "irrigation subsidy drip sprinkler micro irrigation"
        
        result = await rag_tool.search_schemes(
            query=test_query,
            top_k=20,
            top_n_schemes=3
        )
        
        return {
            "test_status": "success",
            "test_query": test_query,
            "rag_available": rag_tool.pinecone_available,
            "result": result
        }
    
    except Exception as e:
        logger.error(f"RAG test failed: {str(e)}")
        return {
            "test_status": "failed",
            "error": str(e),
            "rag_available": rag_tool.pinecone_available
        }


@router.post("/bulk-search")
async def bulk_search_schemes(request: Dict[str, Any]):
    logger.info("======== Bulk Schemes Search API ========")
    
    try:
        queries = request.get("queries", [])
        if not queries or not isinstance(queries, list):
            raise HTTPException(status_code=400, detail="Queries list is required")
        
        top_n_schemes = request.get("top_n_schemes", 3)
        
        results = []
        for i, query in enumerate(queries):
            if not query or not str(query).strip():
                results.append({
                    "query_index": i,
                    "query": query,
                    "success": False,
                    "error": "Empty query"
                })
                continue
            
            result = await rag_tool.search_schemes(
                query=str(query).strip(),
                top_n_schemes=top_n_schemes
            )
            result["query_index"] = i
            results.append(result)
        
        return {
            "success": True,
            "total_queries": len(queries),
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk search failed: {str(e)}")


@router.get("/examples")
async def get_example_queries():
    return {
        "example_queries": [
            "irrigation subsidy schemes",
            "crop insurance for farmers",
            "small farmer loan schemes",
            "drip irrigation financial assistance",
            "storage facility government support",
            "organic farming subsidies",
            "soil testing schemes",
            "equipment purchase subsidy",
            "dairy farming assistance",
            "horticulture development schemes"
        ],
        "example_farmer_context": {
            "crops": ["wheat", "rice"],
            "farmer_type": "small",
            "location": "Punjab",
            "landholding": 2.5
        },
        "api_usage": {
            "search": "POST /api/schemes/search",
            "recommend": "POST /api/schemes/recommend",
            "details": "GET /api/schemes/scheme/{scheme_id}",
            "test": "GET /api/schemes/test"
        }
    }
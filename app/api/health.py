from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["health"]
)

@router.get("/")
async def get_health():
    return {"status": "healthy"}

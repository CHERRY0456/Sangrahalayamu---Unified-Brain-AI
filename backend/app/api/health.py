from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health_check():
    """
    Service health check node validating api connectivity.
    """
    return {"status": "healthy", "service": "Sangrahalayamu Backend API"}

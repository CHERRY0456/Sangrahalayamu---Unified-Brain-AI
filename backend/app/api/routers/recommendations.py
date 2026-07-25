"""
Recommendations router disabled per enterprise requirement.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

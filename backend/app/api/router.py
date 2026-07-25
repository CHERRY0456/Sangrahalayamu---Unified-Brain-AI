from fastapi import APIRouter
from app.api import auth, access, audit, diff
from app.api.routers import upload, chat, graph, agents, health

# NOTE: health router is registered both at root level in main.py (/health)
# and under the /api prefix (/api/health) for maximum compatibility.

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(access.router)
api_router.include_router(audit.router)
api_router.include_router(diff.router)
api_router.include_router(upload.router)
api_router.include_router(chat.router)
api_router.include_router(graph.router)
api_router.include_router(agents.router)
api_router.include_router(health.router)

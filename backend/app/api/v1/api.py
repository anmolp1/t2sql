from fastapi import APIRouter
from app.api.v1.endpoints import auth, database, query

api_router = APIRouter()

# Include health check endpoint
@api_router.get("/health")
async def health_check():
    return {"status": "ok"}

# Include other endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(database.router, prefix="/databases", tags=["databases"])
api_router.include_router(query.router, prefix="/query", tags=["query"]) 
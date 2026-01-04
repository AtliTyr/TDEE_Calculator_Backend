from fastapi import APIRouter
from app.api.v1 import auth, users, calculations

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(calculations.router, prefix="/calculations", tags=["calculations"])
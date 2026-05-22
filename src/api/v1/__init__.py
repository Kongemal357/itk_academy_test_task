from fastapi import APIRouter
from .routes import wallet


api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(wallet.router)
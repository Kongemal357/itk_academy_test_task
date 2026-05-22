import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from src.api.v1 import api_v1_router
from src.api.v1.errors import add_exception_handlers
from src.db import models
from src.db.database import AsyncSessionLocal, close_engine, engine
from src.utils.logger import LoggingMiddleware

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with startup/shutdown events."""
    # Create database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    yield

    await close_engine()


app = FastAPI(lifespan=lifespan, redirect_slashes=False)

app.add_middleware(LoggingMiddleware)
add_exception_handlers(app)
app.include_router(api_v1_router)

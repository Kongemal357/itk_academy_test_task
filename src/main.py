from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1 import api_v1_router
from src.api.v1.errors import add_exception_handlers
from src.db.database import close_engine
from src.utils.logger import LoggingMiddleware, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with startup/shutdown events."""
    setup_logging()
    yield

    await close_engine()


app = FastAPI(lifespan=lifespan, redirect_slashes=False)

app.add_middleware(LoggingMiddleware)
add_exception_handlers(app)
app.include_router(api_v1_router)

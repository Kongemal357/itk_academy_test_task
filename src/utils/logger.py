import logging
import os
from pathlib import Path
from typing import List
from uuid import uuid4

import structlog
import structlog.contextvars
from dotenv import load_dotenv
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

load_dotenv()

# Logging disable setting
LOG_DISABLED = os.getenv("LOG_DISABLED", "false").lower() == "true"

handlers: List[logging.Handler] = [logging.StreamHandler()]  # Console output

if not LOG_DISABLED:
    # File logging setup
    LOG_DIR = Path(os.getenv("LOG_DIR", "/logs"))
    LOG_DIR.mkdir(exist_ok=True, parents=True)

    main_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    error_handler = logging.FileHandler(LOG_DIR / "errors.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)

    handlers.extend([main_handler, error_handler])

# Basic logging configuration
logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
    handlers=handlers,
)

# Structured logging setup
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for HTTP request logging."""

    async def dispatch(self, request: Request, call_next):
        if LOG_DISABLED:
            return await call_next(request)

        request_id = str(uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)

        logger.info("request_started", method=request.method, path=request.url.path)

        try:
            response = await call_next(request)
            logger.info("request_finished", status_code=response.status_code)
            return response
        except Exception as e:
            logger.error("request_failed", error=str(e))
            raise
        finally:
            structlog.contextvars.clear_contextvars()


logger = structlog.get_logger()

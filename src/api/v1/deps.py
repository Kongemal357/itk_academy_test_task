import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import models
from src.db.database import get_session
from src.utils.hash import hash_api_key

load_dotenv()
MEDIA_DIR = Path(os.getenv("MEDIA_DIR", "/media"))

api_key_header = APIKeyHeader(name="api-key")


async def get_user_from_api_key(
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_session),
) -> Optional[int]:
    """Retrieves user ID based on the provided API key.

    Validates the API key by hashing it and searching for a matching record
    in the database. Returns the user ID if the key is valid.

    :param api_key: The API key provided in the request header.
    :type api_key: str
    :param session: Database session for executing the query.
    :type session: AsyncSession

    :return: User ID associated with the valid API key, or None if not found.
    :rtype: Optional[int]

    :raises HTTPException 403: If the provided API key is invalid or not found.

    .. note::
        The API key is hashed before database comparison for security reasons.
        The original key is never stored in the database.

    .. warning::
        This function is used as a dependency injection for authentication
        in protected endpoints. Invalid keys will result in HTTP 403 error.
    """
    hash_key = hash_api_key(api_key)

    user_result = await session.execute(
        select(models.ApiKey.user_id).where(models.ApiKey.hashed_key == hash_key)
    )

    user_id = user_result.scalar_one_or_none()

    if user_id is None:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return user_id


def get_upload_folder() -> str:
    """Retrieves the media upload directory path.

    Returns the path to the directory where media files should be uploaded.
    The path is determined by the MEDIA_DIR environment variable with a
    default fallback to '/media'.

    :return: Absolute path to the media upload directory.
    :rtype: str

    .. note::
        The directory path can be configured using the MEDIA_DIR environment variable.

    .. warning::
        Ensure the specified directory exists and has appropriate write permissions
        for the application process.

    .. seealso::
        :func:`post_medias` for the endpoint that uses this upload directory.
    """
    return str(MEDIA_DIR)

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_db
from app.repositories.user import UserRepository
from app.security.token import TokenError, validate_token_type


bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
):
    """
    Validate the access token and return the current user.
    """

    token = credentials.credentials

    try:
        payload = validate_token_type(
            token,
            expected_type="access",
        )

        user_id = payload.get("sub")

        if not user_id:
            raise TokenError("Token subject is missing")
        try:
            user_id = UUID(user_id)
        except ValueError:
            raise TokenError("Invalid user ID in token")
    except TokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repository = UserRepository(db)

    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
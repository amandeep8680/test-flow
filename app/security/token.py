from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from jwt import InvalidTokenError

from app.core.config import get_settings


settings = get_settings()


class TokenError(Exception):
    """
    Raised when a JWT is invalid or cannot be decoded.
    """

    pass


def create_access_token(
    user_id: UUID,
    organization_id: UUID,
) -> str:
    """
    Create a short-lived JWT access token.
    """

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "organization_id": str(organization_id),
        "type": "access",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(
    user_id: UUID,
    organization_id: UUID,
) -> str:
    """
    Create a long-lived JWT refresh token.
    """

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )

    payload = {
        "sub": str(user_id),
        "organization_id": str(organization_id),
        "type": "refresh",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT.

    Raises:
        TokenError: If the token is invalid or expired.
    """

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        return payload

    except InvalidTokenError as exc:
        raise TokenError("Invalid or expired token") from exc


def get_token_user_id(token: str) -> UUID:
    """
    Extract and validate the user ID from a JWT.
    """

    payload = decode_token(token)

    user_id = payload.get("sub")

    if not user_id:
        raise TokenError("Token subject is missing")

    try:
        return UUID(user_id)
    except ValueError as exc:
        raise TokenError("Invalid user ID in token") from exc


def get_token_organization_id(token: str) -> UUID:
    """
    Extract and validate the organization ID from a JWT.
    """

    payload = decode_token(token)

    organization_id = payload.get("organization_id")

    if not organization_id:
        raise TokenError("Organization ID is missing")

    try:
        return UUID(organization_id)
    except ValueError as exc:
        raise TokenError(
            "Invalid organization ID in token"
        ) from exc


def validate_token_type(
    token: str,
    expected_type: str,
) -> dict:
    """
    Validate JWT and ensure it is the expected token type.

    Example:
        validate_token_type(token, "access")
        validate_token_type(token, "refresh")
    """

    payload = decode_token(token)

    token_type = payload.get("type")

    if token_type != expected_type:
        raise TokenError("Invalid token type")

    return payload
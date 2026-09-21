from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.exception.exceptions import UnauthorizedException
from app.exception.messages import AuthMessages
from app.models.refresh_token import RefreshToken
from app.security.token import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TokenService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tokens(self, user_id, organization_id):
        # Delete existing refresh tokens for this user
        await self.db.execute(
            delete(RefreshToken).where(
                RefreshToken.user_id == user_id
            )
        )

        # Create new tokens
        access_token = create_access_token(
            user_id=user_id,
            organization_id=organization_id,
        )

        refresh_token = create_refresh_token(
            user_id=user_id,
            organization_id=organization_id,
        )

        settings = get_settings()

        refresh_token_record = RefreshToken(
            user_id=user_id,
            token=refresh_token,
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(days=settings.refresh_token_expire_days)
            ),
            revoked=False,
        )

        self.db.add(refresh_token_record)
        await self.db.flush()

        return access_token, refresh_token

    async def refresh_access_token(self, refresh_token: str):
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise UnauthorizedException(
                AuthMessages.INVALID_REFRESH_TOKEN
            )

        if payload.get("type") != "refresh":
            raise UnauthorizedException(
                AuthMessages.INVALID_TOKEN_TYPE
            )

        user_id = payload.get("sub")

        if not user_id:
            raise UnauthorizedException(
                AuthMessages.INVALID_REFRESH_TOKEN
            )

        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token == refresh_token,
                RefreshToken.revoked.is_(False),
            )
        )

        stored_token = result.scalar_one_or_none()

        if stored_token is None:
            raise UnauthorizedException(
                AuthMessages.INVALID_REFRESH_TOKEN
            )

        if stored_token.expires_at <= datetime.now(timezone.utc):
            raise UnauthorizedException(
                AuthMessages.INVALID_REFRESH_TOKEN
            )

        access_token = create_access_token(
            user_id=stored_token.user_id,
            organization_id=payload.get("organization_id"),
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    async def logout(self, refresh_token: str):
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token == refresh_token
            )
        )

        stored_token = result.scalar_one_or_none()

        if stored_token:
            stored_token.revoked = True
            await self.db.commit()

        return {
            "message": AuthMessages.LOGOUT_SUCCESSFUL
        }
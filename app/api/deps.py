from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import InvalidTokenError
from app.core.security import decode_access_token
from app.models.user import User
from app.services.user_service import UserService

# tokenUrl tells Swagger UI where to POST credentials to obtain a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency — resolves the Bearer token from the Authorization header
    and returns the authenticated User.  Raises HTTP 401 on any failure so
    that callers never receive a partially-validated user object.
    """
    username = decode_access_token(token)  # raises InvalidTokenError if bad/expired
    svc = UserService(db)
    user = await svc.get_by_username(username)
    if user is None or not user.is_active:
        raise InvalidTokenError()
    return user

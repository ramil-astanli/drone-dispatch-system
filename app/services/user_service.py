from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InactiveUserError,
    InvalidCredentialsError,
    UsernameAlreadyTakenError,
)
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.base import BaseService


class UserService(BaseService[User]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def register(self, payload: UserCreate) -> User:
        """Hash the password and persist a new user after uniqueness checks."""
        if await self.get_by_username(payload.username):
            raise UsernameAlreadyTakenError(payload.username)
        if await self.get_by_email(payload.email):
            raise EmailAlreadyRegisteredError(payload.email)

        user = User(
            username=payload.username,
            email=str(payload.email),
            hashed_password=hash_password(payload.password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, username: str, password: str) -> User:
        """
        Verify credentials and return the active user.
        Always raises the same generic error for wrong username **or** wrong
        password to prevent user-enumeration attacks.
        """
        user = await self.get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InactiveUserError()
        return user

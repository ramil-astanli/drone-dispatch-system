from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.user import Token, UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    responses={
        409: {"description": "Username or email already taken"},
    },
)
async def signup(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """
    Create a new user account.  The plain-text password is hashed with bcrypt
    before being stored — it is never persisted in cleartext.
    """
    svc = UserService(db)
    return await svc.register(payload)


@router.post(
    "/login",
    response_model=Token,
    summary="Obtain a JWT access token",
    responses={
        401: {"description": "Incorrect username or password"},
        403: {"description": "Account is deactivated"},
    },
)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Authenticate with **username** and **password** (standard OAuth2 form fields).
    Returns a signed JWT Bearer token valid for the configured expiry window.
    """
    svc = UserService(db)
    user = await svc.authenticate(form.username, form.password)
    access_token = create_access_token(subject=user.username)
    return Token(access_token=access_token)

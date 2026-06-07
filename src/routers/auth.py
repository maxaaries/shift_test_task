from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.auth import Token, UserRead, UserRegister
from src.services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegister,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRead:
    service = AuthService(session)
    user = await service.register(payload)
    return UserRead.model_validate(user)


@auth_router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Token:
    service = AuthService(session)
    access_token = await service.login(form_data.username, form_data.password)
    return Token(access_token=access_token)

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.jwt import create_access_token
from src.core.security import hash_password, verify_password
from src.models.user import ROLE_EMPLOYEE, User
from src.repositories.user_repository import UserRepository
from src.schemas.auth import UserRegister


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repository = UserRepository(session)

    async def register(self, payload: UserRegister) -> User:
        existing_user = await self.user_repository.get_by_email(payload.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует",
            )

        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            role=ROLE_EMPLOYEE,
        )
        created_user = await self.user_repository.add(user)
        await self.session.commit()
        return created_user

    async def login(self, email: str, password: str) -> str:
        user = await self.user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return create_access_token(user.id)

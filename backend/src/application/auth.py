import os
from typing import Optional

from fastapi import Depends, Request, exceptions
from fastapi_users import FastAPIUsers, IntegerIDMixin, BaseUserManager, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType

from infrastructure.database import UserModel
from infrastructure.user_db import get_user_db
from passlib.context import CryptContext

SECRET = os.getenv("JWT_SECRET")
if not SECRET:
    raise ValueError("JWT_SECRET not set!")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto",
                           argon2__memory_cost=65536,
                           argon2__time_cost=3,
                           argon2__parallelism=4)

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("SMTP_USER"),
    MAIL_PASSWORD=os.getenv("SMTP_PASSWORD"),
    MAIL_FROM=os.getenv("FROM_EMAIL"),
    MAIL_PORT=int(os.getenv("SMTP_PORT", 587)),
    MAIL_SERVER=os.getenv("SMTP_HOST"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

mail = FastMail(conf)

class UserManager(IntegerIDMixin, BaseUserManager[UserModel, int]):
    """
    Custom user manager to handle user operations.
    """
    user_db_model = UserModel
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def validate_password(
        self,
        password: str,
        user: models.UP,
    ) -> None:
        if len(password) < 8:
            raise exceptions.InvalidPasswordException("Password should be at least 8 characters")

    async def on_after_register(self, user: models.UP, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        return pwd_context.verify(password, hashed_password)
    
    async def on_after_forgot_password(
        self, user: UserModel, token: str, _: Optional[Request] = None
    ):
        message = MessageSchema(
            subject="Reset Password Clean Barcode",
            recipients=[user.email],
            body=f"Password reset token: {token}",
            subtype=MessageType.plain
        )
        await mail.send_mail(message)
        print(f"Password reset email has been sent to user {user.id}")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=60 * 30)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="auth/jwt/login"),
    get_strategy=get_jwt_strategy,
)

def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    return UserManager(user_db)

fastapi_users = FastAPIUsers[UserModel, int](
    get_user_manager,
    [auth_backend]
)

current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
"""
User database dependency.
"""
from fastapi.params import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import UserModel, get_db_session

async def get_user_db(session: AsyncSession = Depends(get_db_session)):
    """
    Get the user database instance.
    """
    yield SQLAlchemyUserDatabase(session, UserModel)
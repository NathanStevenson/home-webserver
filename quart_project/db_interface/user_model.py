from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column
from .base_model import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    # default constructor (email, password, username)
    def __init__(self, email, hashed_password, username, phone_number="XXX-XXX-XXXX", user_profile_path="default_profile.png"):
        self.email = email
        self.hashed_password = hashed_password
        self.username = username
        self.phone_number = phone_number
        self.user_profile_path = user_profile_path
    
    # mapped column is preferred over column in modern sql alchemy due to typing
    # mapped column you declare the type inside Mapped[] and it works better for type checking; cleaner code; designed for modern sql alchemy as compared to classic Column()

    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    phone_number: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column()
    user_profile_path: Mapped[str] = mapped_column() 

    # profile_image; posts; messages; items; payment method; misc items -- all should be optional (this will need to be rendered by jinja with fields based on config given)
    
    # gets the user by their unique email; will return first found (email is unique) or None - never throws an Exception
    @classmethod
    async def get_user_by_email(cls, session: AsyncSession, email: str):
        result = await session.execute(select(cls).filter_by(email=email))
        return result.scalars().first()
    
    # gets the user by their unique username; will return first found or None - never throws an Exception
    @classmethod
    async def get_user_by_username(cls, session: AsyncSession, username: str):
        result = await session.execute(select(cls).filter_by(username=username))
        return result.scalars().first()

    # gets the user by their unique phone number; will return first found or None - never throws an Exception
    @classmethod
    async def get_user_by_phone_number(cls, session: AsyncSession, phone_number: str):
        result = await session.execute(select(cls).filter_by(phone_number=phone_number))
        return result.scalars().first()
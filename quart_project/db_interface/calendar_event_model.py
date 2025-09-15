from sqlalchemy.orm import Mapped, mapped_column, selectinload
from .base_model import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, select

class CalendarEvent(BaseModel):
    __tablename__ = "calendar_event"

    # default constructor (day, month, year, title, descr)
    def __init__(self, day, month, year, title, description, user_id):
        self.day = day
        self.month = month
        self.year = year
        self.title = title
        self.description = description
        self.user_id = user_id
    
    # mapped column is preferred over column in modern sql alchemy due to typing
    day:            Mapped[str] = mapped_column()
    month:          Mapped[str] = mapped_column()
    year:           Mapped[str] = mapped_column()
    title:          Mapped[str] = mapped_column()
    description:    Mapped[str] = mapped_column()

    # ForeignKey to link back to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # gets all the users along with the events - all in one go no weird async db accessing after the fact
    @classmethod
    async def get_all_with_users(cls, session):
        result = await session.execute(select(cls).options(selectinload(cls.user)))
        return result.scalars().all()
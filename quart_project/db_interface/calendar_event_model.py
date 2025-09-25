from sqlalchemy.orm import Mapped, mapped_column, selectinload
from .base_model import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, select

class CalendarEvent(BaseModel):
    __tablename__ = "calendar_event"

    # default constructor (minute, hour, day, month, year, title, descr)
    def __init__(self, minute, hour, day, month, year, title, description, user_id):
        self.minute = minute
        self.hour = hour
        self.day = day
        self.month = month
        self.year = year
        self.title = title
        self.description = description
        self.user_id = user_id
    
    # mapped column is preferred over column in modern sql alchemy due to typing
    minute:         Mapped[str] = mapped_column()
    hour:           Mapped[str] = mapped_column()
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
    
    # get all the events + corresponding user for a given day/month/year
    @classmethod
    async def get_al_events_for_day(cls, session, day, month, year):
        result = await session.execute(select(cls).options(selectinload(cls.user)).filter_by(day=str(day), month=str(month), year=str(year)))
        return result.scalars().all()
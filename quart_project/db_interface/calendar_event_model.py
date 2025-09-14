from sqlalchemy.orm import Mapped, mapped_column
from .base_model import BaseModel

class CalendarEvent(BaseModel):
    __tablename__ = "calendar_event"

    # default constructor (day, month, year, title, descr)
    def __init__(self, day, month, year, title, description):
        self.day = day
        self.month = month
        self.year = year
        self.title = title
        self.description = description
    
    # mapped column is preferred over column in modern sql alchemy due to typing
    day:            Mapped[str] = mapped_column()
    month:          Mapped[str] = mapped_column()
    year:           Mapped[str] = mapped_column()
    title:          Mapped[str] = mapped_column()
    description:    Mapped[str] = mapped_column() 
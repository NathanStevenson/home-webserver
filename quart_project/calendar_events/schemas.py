from pydantic import BaseModel
from typing import Optional

class CalendarEvent(BaseModel):
    minute: str
    hour: str
    day: str
    month: str
    year: str
    title: str
    description: str
    id: Optional[int]
from pydantic import BaseModel
from typing import Optional

class CalendarEvent(BaseModel):
    day: str
    month: str
    year: str
    title: str
    description: str
    id: Optional[int]
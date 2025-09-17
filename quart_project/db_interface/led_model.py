from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column
from .base_model import BaseModel

class LED_Device(BaseModel):
    __tablename__ = "leds"

    # default constructor (name, ip_address, message, color, text_wrap, port)
    def __init__(self, name, ip_address, message="Hello World", color="(0, 0, 255)", text_wrap=True, port="8000", display_type="message"):
        self.name = name
        self.ip_address = ip_address
        self.message = message
        self.color = color
        self.text_wrap = text_wrap
        self.port = port
        self.display_type = display_type # message, weather, calendar, clock
    
    # mapped column is preferred over column in modern sql alchemy due to typing
    name:           Mapped[str]     = mapped_column(unique=True)
    ip_address:     Mapped[str]     = mapped_column(unique=True)
    message:        Mapped[str]     = mapped_column()
    color:          Mapped[str]     = mapped_column()
    text_wrap:      Mapped[bool]    = mapped_column() 
    port:           Mapped[str]     = mapped_column() 
    display_type:   Mapped[str]     = mapped_column() 

    # gets the led by its unique username; will return first found or None - never throws an Exception
    @classmethod
    async def get_device_by_name(cls, session: AsyncSession, name: str):
        result = await session.execute(select(cls).filter_by(name=name))
        return result.scalars().first()
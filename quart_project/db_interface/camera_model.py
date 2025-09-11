from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column
from .base_model import BaseModel

class Camera(BaseModel):
    __tablename__ = "camera"

     # default constructor (email, password, username)
    def __init__(self, location, ip_address, port="8080"):
        self.location = location
        self.ip_address = ip_address
        self.port = port
    
    # All of the cameras needed specific attributes
    location: Mapped[str] = mapped_column()
    ip_address: Mapped[str] = mapped_column() 
    port: Mapped[str] = mapped_column() 

    # Use Base.get_by_id() to get the camera does not need custom getters
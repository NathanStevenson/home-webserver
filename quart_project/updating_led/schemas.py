from pydantic import BaseModel

class UpdateLedScreen(BaseModel):
    # weather, clock, message, calendar
    pi_name: str
    message: str
    color: str
    wrap_text: bool

class ChangeDisplay(BaseModel):
    # weather, clock, message, calendar
    display_type: str  
    pi_name: str
    color: str
    wrap_text: bool
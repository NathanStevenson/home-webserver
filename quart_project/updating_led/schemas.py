from pydantic import BaseModel

class UpdateLedScreen(BaseModel):
    pi_name: str
    message: str
    color: str
    wrapText: bool
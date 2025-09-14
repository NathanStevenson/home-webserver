from pydantic import BaseModel

class UpdateLedScreen(BaseModel):
    pi_name: str
    message: str
    color: str
    wrap_text: bool
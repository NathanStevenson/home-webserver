from pydantic import BaseModel

class UpdateLedScreen(BaseModel):
    message: str
    color: str
    wrap_text: bool
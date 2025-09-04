from pydantic import BaseModel, EmailStr

class ResetPassword(BaseModel):
    username: str
    password: str
    password_verify: str

class UserLogin(BaseModel):
    username: str
    password: str
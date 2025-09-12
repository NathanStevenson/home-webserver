from pydantic import BaseModel, EmailStr

class ResetPassword(BaseModel):
    username: str
    password: str
    password_verify: str

class UserLogin(BaseModel):
    username: str
    password: str

class ApplyChanges(BaseModel):
    username: str
    email: EmailStr
    phone_number: str
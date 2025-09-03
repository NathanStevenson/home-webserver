from pydantic import BaseModel, EmailStr

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str
    password_verify: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
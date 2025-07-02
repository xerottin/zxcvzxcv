from pydantic import BaseModel, EmailStr




class User(BaseModel):
    username: str

class UserInDB(User):
    password: str
    email: EmailStr
    phone: str
    is_verified: bool

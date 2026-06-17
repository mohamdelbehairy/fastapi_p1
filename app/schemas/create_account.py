from pydantic import BaseModel, EmailStr, Field

class CreateAccount(BaseModel):
    fullName: str
    email: EmailStr
    age: int
    password: str = Field(..., min_length=6, max_length=20)

from pydantic import BaseModel, EmailStr

class EditUserData(BaseModel):
    fullName: str | None = None
    email: EmailStr | None = None
    age: int | None = None
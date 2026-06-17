from sqlmodel import SQLModel, Field
from uuid import uuid4
from pydantic import EmailStr

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    fullName: str
    email: EmailStr = Field(unique=True, index=True)
    age: int | None = None
    password: str

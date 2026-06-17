from pydantic import BaseModel
class RefreshTokenLogic(BaseModel):
    refresh_token: str
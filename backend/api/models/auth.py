from pydantic import BaseModel


class TokenClaims(BaseModel):
    user_id: str
    email: str
    email_verified: bool

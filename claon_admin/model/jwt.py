from pydantic import BaseModel


class JwtResponseDto(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

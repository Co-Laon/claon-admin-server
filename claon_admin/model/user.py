from pydantic import BaseModel


class UserRequestDto(BaseModel):
    email: str
    username: str
    password: str


class UserResponseDto(BaseModel):
    id: str
    email: str
    username: str
    password: str
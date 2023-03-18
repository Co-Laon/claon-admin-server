from pydantic import BaseModel


class ExampleRequestDto(BaseModel):
    name: str


class ExampleResponseDto(BaseModel):
    id: str
    name: str

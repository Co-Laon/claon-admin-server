from pydantic import BaseModel


class ExamplePropertyDto(BaseModel):
    name: str
    description: str


class ExampleRequestDto(BaseModel):
    name: str
    prop: ExamplePropertyDto


class ExampleResponseDto(BaseModel):
    id: str
    name: str
    prop: ExamplePropertyDto

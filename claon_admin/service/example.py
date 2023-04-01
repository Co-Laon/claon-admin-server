from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.model.example import ExampleRequestDto, ExampleResponseDto, ExamplePropertyDto
from claon_admin.schema.example import ExampleRepository, Example, ExampleProperty


class ExampleService:
    def __init__(self, example_repository: ExampleRepository):
        self.example_repository = example_repository

    async def find_by_id(self, session: AsyncSession, example_id: str):
        example = await self.example_repository.find_by_id(session, example_id)

        return ExampleResponseDto(
            id=example.id,
            name=example.name,
            prop=ExamplePropertyDto(name=example.prop.name, description=example.prop.description)
        )

    async def save(self, session: AsyncSession, request_dto: ExampleRequestDto):
        example = Example(
            name=request_dto.name,
            prop=ExampleProperty(name=request_dto.prop.name, description=request_dto.prop.description)
        )
        example = await self.example_repository.save(session, example)

        return ExampleResponseDto(
            id=example.id,
            name=example.name,
            prop=ExamplePropertyDto(name=example.prop.name, description=example.prop.description)
        )

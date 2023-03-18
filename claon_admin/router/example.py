from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.container import Container, db
from claon_admin.model.example import ExampleResponseDto, ExampleRequestDto
from claon_admin.service.example import ExampleService

router = APIRouter()


@cbv(router)
class ExampleRouter:
    @inject
    def __init__(self,
                 example_service: ExampleService = Depends(Provide[Container.example_service])):
        self.example_service = example_service

    @router.get('/example/{example_id}', response_model=ExampleResponseDto)
    async def find_by_id(self,
                         example_id: str,
                         session: AsyncSession = Depends(db.get_db)):
        return await self.example_service.find_by_id(session, example_id)

    @router.post('/example', response_model=ExampleResponseDto)
    async def save(self,
                   request_dto: ExampleRequestDto,
                   session: AsyncSession = Depends(db.get_db)):
        return await self.example_service.save(session, request_dto)

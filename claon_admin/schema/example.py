from uuid import uuid4

from sqlalchemy import Column, String, select
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.conn import Base


class Example(Base):
    __tablename__ = 'tb_example'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    name = Column(String(length=255))


class ExampleRepository:
    @staticmethod
    async def find_by_id(session: AsyncSession, example_id: str):
        result = await session.execute(select(Example).where(Example.id == example_id))
        return result.scalars().one_or_none()

    @staticmethod
    async def save(session: AsyncSession, example: Example):
        session.add(example)
        await session.flush()
        return example

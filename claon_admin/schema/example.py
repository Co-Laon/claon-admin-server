import json
from uuid import uuid4

from sqlalchemy import Column, String, select
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.conn import Base


class ExampleProperty:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


class Example(Base):
    __tablename__ = 'tb_example'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    name = Column(String(length=255))
    _prop = Column(String(length=255))

    @property
    def prop(self):
        data = json.loads(self._prop)
        return ExampleProperty(data['name'], data['description'])

    @prop.setter
    def prop(self, value: ExampleProperty):
        self._prop = json.dumps(value.__dict__)


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

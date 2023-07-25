from typing import TypeVar, Generic, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class Repository(Generic[T]):
    __orig_bases__ = Generic[T]

    async def find_by_id(self, session: AsyncSession, entity_id):
        entity_class = self.__orig_bases__[0].__args__[0]
        print("LOG:", self.__orig_bases__, self.__orig_bases__[0].__args__)
        result = await session.execute(select(entity_class).where(entity_class.id == entity_id))
        return result.scalars().one_or_none()

    async def save(self, session: AsyncSession, entity: T):
        session.add(entity)
        await session.merge(entity)
        return entity

    async def save_all(self, session: AsyncSession, entity_list: List[T]):
        session.add_all(entity_list)
        [await session.merge(entity) for entity in entity_list]
        return entity_list

    async def delete(self, session: AsyncSession, entity: T):
        return await session.delete(entity)

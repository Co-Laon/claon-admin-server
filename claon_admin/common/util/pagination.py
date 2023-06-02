from typing import TypeVar, Generic, List, Type

from fastapi_pagination import Page
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar('T', bound=BaseModel)


class Pagination(GenericModel, Generic[T]):
    next_page_num: int
    previous_page_num: int
    total_num: int
    results: List[T]


S = TypeVar('S')


async def paginate(t: Type[T], p: Page[S]):
    return Pagination(
        next_page_num=__build_next_page(p),
        previous_page_num=__build_previous_page(p),
        total_num=p.total,
        results=[t.from_entity(item) for item in p.items]
    )


def __build_next_page(p: Page[S]):
    if p.pages - 1 < p.page + 1:
        return -1

    return min(p.page + 1, max(p.pages - 1, 0))


def __build_previous_page(p: Page[S]):
    if p.page - 1 < 0:
        return -1

    return max(0, p.page - 1)

import json
from datetime import date
from typing import List
from uuid import uuid4

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Column, String, DateTime, TEXT, ForeignKey, Integer, Enum, and_, select, desc, func, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, backref, selectinload

from claon_admin.common.enum import WallType
from claon_admin.common.util.db import Base
from claon_admin.common.util.repository import Repository


class PostImage:
    def __init__(self, url: str):
        self.url = url


class Post(Base):
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    content = Column(String(length=500), nullable=False)
    _img = Column(TEXT, nullable=False)
    histories = relationship("ClimbingHistory", back_populates="post", cascade="all, delete-orphan")

    user_id = Column(String(length=255), ForeignKey("tb_user.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref=backref("Post"))
    center_id = Column(String(length=255), ForeignKey("tb_center.id", ondelete="CASCADE"), nullable=False)
    center = relationship("Center", backref=backref("Post"))

    @property
    def img(self):
        if self._img is None:
            return []

        values = json.loads(self._img)
        return [PostImage(value['url']) for value in values]

    @img.setter
    def img(self, values: List[PostImage]):
        self._img = json.dumps([value.__dict__ for value in values], default=str)


class ClimbingHistory(Base):
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    hold_id = Column(String(length=255), nullable=False)
    difficulty = Column(String(length=10), nullable=False)
    challenge_count = Column(Integer, nullable=False)
    wall_name = Column(String(length=20), nullable=False)
    wall_type = Column(Enum(WallType), nullable=False)

    post_id = Column(String(length=255), ForeignKey("tb_post.id", ondelete="CASCADE"), nullable=False)
    post = relationship("Post", back_populates="histories")


class PostCountHistory(Base):
    id = Column(Integer, primary_key=True, index=True)
    center_id = Column(String(length=255), nullable=False)
    reg_date = Column(DateTime, nullable=False)
    count = Column(Integer, nullable=False)


class PostRepository(Repository[Post]):
    async def find_posts_by_center(self,
                                   session: AsyncSession,
                                   params: Params,
                                   center_id: str,
                                   hold_id: str | None,
                                   start: date,
                                   end: date):
        query = select(Post).where(and_(Post.center_id == center_id,
                                        Post.created_at >= start,
                                        Post.created_at < end))

        if hold_id is not None:
            query = query \
                .join(ClimbingHistory) \
                .where(ClimbingHistory.hold_id == hold_id)

        query = query.order_by(desc(Post.created_at)).options(selectinload(Post.user))

        return await paginate(query=query, conn=session, params=params)

    async def count_by_center_and_date(self, session: AsyncSession, center_ids: List[str], start: date, end: date):
        query_result = await session.execute(select(Post.center_id, func.count(Post.id))
                                             .where(and_(Post.center_id.in_(center_ids),
                                                         Post.created_at >= start,
                                                         Post.created_at < end))
                                             .group_by(Post.center_id))
        return {center_id: count for center_id, count in query_result.fetchall()}


class ClimbingHistoryRepository(Repository[ClimbingHistory]):
    pass


class PostCountHistoryRepository(Repository[PostCountHistory]):
    async def sum_count_by_center(self, session: AsyncSession, center_id: str):
        result = await session.execute(select(func.sum(PostCountHistory.count))
                                       .where(PostCountHistory.center_id == center_id)
                                       .order_by(desc(PostCountHistory.reg_date)))
        return result.scalars().first() or 0

    async def find_by_center_and_date(self, session: AsyncSession, center_id: str, start: date, end: date):
        result = await session.execute(select(PostCountHistory)
                                       .where(and_(PostCountHistory.center_id == center_id,
                                                   PostCountHistory.reg_date >= start,
                                                   PostCountHistory.reg_date < end))
                                       .order_by(asc(PostCountHistory.reg_date)))
        return result.scalars().all()

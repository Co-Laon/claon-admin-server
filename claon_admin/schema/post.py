import json
from datetime import date, timedelta, datetime
from typing import List, Optional
from uuid import uuid4

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Column, String, DateTime, TEXT, ForeignKey, Integer, Enum, and_, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, backref, selectinload

from claon_admin.common.enum import WallType
from claon_admin.common.util.db import Base
from claon_admin.common.util.time import now


class PostImage:
    def __init__(self, url: str):
        self.url = url


class Post(Base):
    __tablename__ = 'tb_post'
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    content = Column(String(length=500), nullable=False)
    created_at = Column(DateTime, nullable=False)
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
    __tablename__ = 'tb_climbing_history'
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    hold_id = Column(String(length=255), nullable=False)
    difficulty = Column(String(length=10), nullable=False)
    challenge_count = Column(Integer, nullable=False)
    wall_name = Column(String(length=20), nullable=False)
    wall_type = Column(Enum(WallType), nullable=False)

    post_id = Column(String(length=255), ForeignKey("tb_post.id", ondelete="CASCADE"), nullable=False)
    post = relationship("Post", back_populates="histories")


class PostRepository:
    @staticmethod
    async def save(session: AsyncSession, post: Post):
        session.add(post)
        await session.merge(post)
        return post

    @staticmethod
    async def find_posts_by_center(session: AsyncSession,
                                   params: Params,
                                   center_id: str,
                                   hold_id: Optional[str],
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

    @staticmethod
    async def find_posts_summary_by_center(session: AsyncSession, center_id: str):
        counts = dict()
        end_date = now()
        criteria = ["today", "week", "month", "total", "per_day", "per_week"]

        for c in criteria:
            if c == "total":
                query = select(func.count(Post.id)).where(Post.center_id == center_id)
                result = await session.execute(query)
                counts[c] = result.scalar()

            elif c == "today":
                query = select(func.count(Post.id)) \
                    .where(and_(Post.center_id == center_id,
                                Post.created_at >= datetime(end_date.year, end_date.month, end_date.day)))
                result = await session.execute(query)
                counts[c] = result.scalar()

            elif c == "week" or c == "month":
                days = 7 if c == "week" else 30
                start_date = end_date - timedelta(days=days)
                query = select(func.count(Post.id)) \
                    .where(and_(Post.center_id == center_id,
                                Post.created_at.between(start_date, end_date)))
                result = await session.execute(query)
                counts[c] = result.scalar()

            elif c == "per_day" or c == "per_week":
                days = 7 if c == "per_day" else 365
                start_date = end_date - timedelta(days=days)
                query = select(Post.id, Post.created_at) \
                    .where(Post.created_at.between(start_date, end_date)) \
                    .order_by(desc(Post.created_at))
                result = await session.execute(query)
                counts[c] = result.fetchall()

        return counts


class ClimbingHistoryRepository:
    @staticmethod
    async def save(session: AsyncSession, history: ClimbingHistory):
        session.add(history)
        await session.merge(history)
        return history

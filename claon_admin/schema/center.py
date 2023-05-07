import json
from datetime import date
from typing import List, Optional
from uuid import uuid4

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import String, Column, ForeignKey, Boolean, select, exists, Integer, DateTime, Enum, delete, and_, desc, \
    func, or_, null, not_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload, backref, aliased
from sqlalchemy.dialects.postgresql import TEXT

from claon_admin.common.enum import PeriodType, MembershipType, WallType
from claon_admin.common.util.db import Base


class OperatingTime:
    def __init__(self, day_of_week: str, start_time: str, end_time: str):
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time


class Utility:
    def __init__(self, name: str):
        self.name = name


class CenterImage:
    def __init__(self, url: str):
        self.url = url


class CenterFeeImage:
    def __init__(self, url: str):
        self.url = url


class PostImage:
    def __init__(self, url: str):
        self.url = url


class ReviewTag:
    def __init__(self, word: str):
        self.word = word


class Center(Base):
    __tablename__ = 'tb_center'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    name = Column(String(length=30), nullable=False)
    profile_img = Column(TEXT, nullable=False)
    address = Column(String(length=255), nullable=False)
    detail_address = Column(String(length=255))
    tel = Column(String(length=255), nullable=False)
    web_url = Column(String(length=500))
    instagram_name = Column(String(length=20))
    youtube_url = Column(String(length=500))
    approved = Column(Boolean, default=False, nullable=False)

    _center_img = Column(TEXT)
    _operating_time = Column(TEXT)
    _utility = Column(TEXT)
    _fee_img = Column(TEXT)

    fees = relationship("CenterFee", back_populates="center", cascade="all, delete-orphan")
    holds = relationship("CenterHold", back_populates="center", cascade="all, delete-orphan")
    walls = relationship("CenterWall", back_populates="center", cascade="all, delete-orphan")

    user_id = Column(String(length=255), ForeignKey("tb_user.id", ondelete="SET NULL"))
    user = relationship("User", backref=backref("Center"))

    @property
    def center_img(self):
        if self._center_img is None:
            return []

        values = json.loads(self._center_img)
        return [CenterImage(value['url']) for value in values]

    @center_img.setter
    def center_img(self, values: List[CenterImage]):
        self._center_img = json.dumps([value.__dict__ for value in values], default=str)

    @property
    def operating_time(self):
        if self._operating_time is None:
            return []

        values = json.loads(self._operating_time)
        return [OperatingTime(value['day_of_week'], value['start_time'], value['end_time']) for value in values]

    @operating_time.setter
    def operating_time(self, values: List[OperatingTime]):
        self._operating_time = json.dumps([value.__dict__ for value in values], default=str)

    @property
    def utility(self):
        if self._utility is None:
            return []

        values = json.loads(self._utility)
        return [Utility(value['name']) for value in values]

    @utility.setter
    def utility(self, values: List[Utility]):
        self._utility = json.dumps([value.__dict__ for value in values], default=str)

    @property
    def fee_img(self):
        if self._fee_img is None:
            return []

        data = json.loads(self._fee_img)
        return [CenterFeeImage(e['url']) for e in data]

    @fee_img.setter
    def fee_img(self, values: List[CenterFeeImage]):
        self._fee_img = json.dumps([value.__dict__ for value in values], default=str)


class CenterFee(Base):
    __tablename__ = 'tb_center_fee'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    name = Column(String(length=50), nullable=False)
    membership_type = Column(Enum(MembershipType), nullable=False)
    price = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)
    period_type = Column(Enum(PeriodType), nullable=False)

    center_id = Column(String(length=255), ForeignKey('tb_center.id', ondelete="CASCADE"), nullable=False)
    center = relationship("Center", back_populates="fees")


class CenterHold(Base):
    __tablename__ = 'tb_center_hold'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    name = Column(String(length=10))
    difficulty = Column(String(length=10))
    is_color = Column(Boolean, default=False, nullable=False)
    img = Column(TEXT, nullable=False)

    center_id = Column(String(length=255), ForeignKey('tb_center.id', ondelete="CASCADE"), nullable=False)
    center = relationship("Center", back_populates="holds")


class CenterWall(Base):
    __tablename__ = 'tb_center_wall'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    name = Column(String(length=20))
    type = Column(String(length=20))

    center_id = Column(String(length=255), ForeignKey('tb_center.id', ondelete="CASCADE"), nullable=False)
    center = relationship("Center", back_populates="walls")


class CenterApprovedFile(Base):
    __tablename__ = 'tb_center_approved_file'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    url = Column(String(length=255))

    user_id = Column(String(length=255), ForeignKey('tb_user.id', ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref=backref("CenterApprovedFile", passive_deletes=True))
    center_id = Column(String(length=255), ForeignKey('tb_center.id', ondelete="CASCADE"), nullable=False)
    center = relationship("Center", backref=backref("CenterApprovedFile", cascade="all,delete"))


class Post(Base):
    __tablename__ = 'tb_post'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
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
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    hold_id = Column(String(length=255), nullable=False)
    hold_url = Column(TEXT, nullable=False)
    difficulty = Column(String(length=10), nullable=False)
    challenge_count = Column(Integer, nullable=False)
    wall_name = Column(String(length=20), nullable=False)
    wall_type = Column(Enum(WallType), nullable=False)

    post_id = Column(String(length=255), ForeignKey("tb_post.id", ondelete="CASCADE"), nullable=False)
    post = relationship("Post", back_populates="histories")


class Review(Base):
    __tablename__ = "tb_review"
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    content = Column(String(length=500), nullable=False)
    created_at = Column(DateTime, nullable=False)
    _tag = Column(TEXT, nullable=False)
    answer = relationship("ReviewAnswer", back_populates="review", uselist=False, cascade="all, delete-orphan")

    user_id = Column(String(length=255), ForeignKey("tb_user.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref=backref("Review"))
    center_id = Column(String(length=255), ForeignKey("tb_center.id", ondelete="CASCADE"), nullable=False)
    center = relationship("Center", backref=backref("Review"))

    @property
    def tag(self):
        if self._tag is None:
            return []

        values = json.loads(self._tag)
        return [ReviewTag(value['word']) for value in values]

    @tag.setter
    def tag(self, values: List[ReviewTag]):
        self._tag = json.dumps([value.__dict__ for value in values], default=str)


class ReviewAnswer(Base):
    __tablename__ = 'tb_review_answer'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    content = Column(String(length=500), nullable=False)
    created_at = Column(DateTime, nullable=False)

    review_id = Column(String(length=255), ForeignKey("tb_review.id", ondelete="CASCADE"), nullable=False)
    review = relationship("Review", back_populates="answer")


class CenterRepository:
    @staticmethod
    async def save(session: AsyncSession, center: Center):
        session.add(center)
        await session.merge(center)
        return center

    @staticmethod
    async def find_by_id(session: AsyncSession, center_id: str):
        result = await session.execute(select(Center).where(Center.id == center_id)
                                       .options(selectinload(Center.holds))
                                       .options(selectinload(Center.walls)))
        return result.scalars().one_or_none()

    @staticmethod
    async def exists_by_id(session: AsyncSession, center_id: str):
        result = await session.execute(select(exists().where(Center.id == center_id)))
        return result.scalar()

    @staticmethod
    async def approve(session: AsyncSession, center: Center):
        center.approved = True
        await session.merge(center)
        return center

    @staticmethod
    async def delete(session: AsyncSession, center: Center):
        return await session.delete(center)

    @staticmethod
    async def find_all_by_approved_false(session: AsyncSession):
        result = await session.execute(select(Center).where(Center.approved == False)
                                       .options(selectinload(Center.user))
                                       .options(selectinload(Center.holds))
                                       .options(selectinload(Center.walls))
                                       .options(selectinload(Center.fees)))
        return result.scalars().all()


class CenterApprovedFileRepository:
    @staticmethod
    async def save(session: AsyncSession, center_approved_file: CenterApprovedFile):
        session.add(center_approved_file)
        await session.merge(center_approved_file)
        return center_approved_file

    @staticmethod
    async def save_all(session: AsyncSession, center_approved_files: List[CenterApprovedFile]):
        session.add_all(center_approved_files)
        [await session.merge(e) for e in center_approved_files]
        return center_approved_files

    @staticmethod
    async def find_all_by_center_id(session: AsyncSession, center_id: str):
        result = await session.execute(select(CenterApprovedFile).where(CenterApprovedFile.center_id == center_id))
        return result.scalars().all()

    @staticmethod
    async def delete_all_by_center_id(session: AsyncSession, center_id: str):
        await session.execute(delete(CenterApprovedFile).where(CenterApprovedFile.center_id == center_id))


class CenterHoldRepository:
    @staticmethod
    async def save(session: AsyncSession, center_hold: CenterHold):
        session.add(center_hold)
        await session.merge(center_hold)
        return center_hold

    @staticmethod
    async def save_all(session: AsyncSession, center_holds: List[CenterHold]):
        session.add_all(center_holds)
        [await session.merge(e) for e in center_holds]
        return center_holds

    @staticmethod
    async def find_all_by_center_id(session: AsyncSession, center_id: str):
        result = await session.execute(select(CenterHold).where(CenterHold.center_id == center_id))
        return result.scalars().all()


class CenterWallRepository:
    @staticmethod
    async def save(session: AsyncSession, center_wall: CenterWall):
        session.add(center_wall)
        await session.merge(center_wall)
        return center_wall

    @staticmethod
    async def save_all(session: AsyncSession, center_walls: List[CenterWall]):
        session.add_all(center_walls)
        [await session.merge(e) for e in center_walls]
        return center_walls

    @staticmethod
    async def find_all_by_center_id(session: AsyncSession, center_id: str):
        result = await session.execute(select(CenterWall).where(CenterWall.center_id == center_id))
        return result.scalars().all()


class CenterFeeRepository:
    @staticmethod
    async def save(session: AsyncSession, center_fee: CenterFee):
        session.add(center_fee)
        await session.merge(center_fee)
        return center_fee

    @staticmethod
    async def save_all(session: AsyncSession, center_fees: List[CenterFee]):
        session.add_all(center_fees)
        [await session.merge(e) for e in center_fees]
        return center_fees

    @staticmethod
    async def find_all_by_center_id(session: AsyncSession, center_id: str):
        result = await session.execute(select(CenterFee).where(CenterFee.center_id == center_id))
        return result.scalars().all()


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
        if hold_id is not None:
            query = select(Post) \
                .join(ClimbingHistory) \
                .where(and_(Post.center_id == center_id,
                            Post.created_at.between(start, end),
                            ClimbingHistory.hold_id == hold_id)) \
                .order_by(desc(Post.created_at)) \
                .options(selectinload(Post.user))

            return await paginate(query=query, conn=session, params=params)

        else:
            query = select(Post) \
                .where(and_(Post.center_id == center_id,
                            Post.created_at.between(start, end))) \
                .order_by(desc(Post.created_at)) \
                .options(selectinload(Post.user))

            return await paginate(query=query, conn=session, params=params)


class ReviewRepository:
    @staticmethod
    async def save(session: AsyncSession, review: Review):
        session.add(review)
        await session.merge(review)
        return review

    @staticmethod
    async def find_reviews_by_center(session: AsyncSession,
                                     params: Params,
                                     center_id: str,
                                     start: date,
                                     end: date,
                                     tag: Optional[str],
                                     is_answered: Optional[bool]):
        post_aliased = aliased(Post)
        center_aliased = aliased(Center)
        review_answer_aliased = aliased(ReviewAnswer)
        query = select(Review, func.count(Post.id)) \
            .select_from(Review) \
            .join(center_aliased, Review.center_id == center_aliased.id) \
            .join(post_aliased, and_(Review.user_id == post_aliased.user_id, Review.center_id == post_aliased.center_id)) \
            .outerjoin(review_answer_aliased, review_answer_aliased.review_id == Review.id) \
            .where(and_(Review.center_id == center_id, Review.created_at.between(start, end))) \
            .group_by(Review.id) \
            .order_by(desc(Review.created_at)) \
            .options(selectinload(Review.user))

        if tag is not None:
            query = query.where(Review._tag.like(f'%{{"word": "{tag}"%'))

        if is_answered is not None:
            if is_answered is False:
                query = query.where(Review.answer == None)
            else:
                query = query.where(Review.answer != None)

        return await paginate(query=query, conn=session, params=params)


class ReviewAnswerRepository:
    @staticmethod
    async def save(session: AsyncSession, answer: ReviewAnswer):
        session.add(answer)
        await session.merge(answer)
        return answer


class ClimbingHistoryRepository:
    @staticmethod
    async def save(session: AsyncSession, history: ClimbingHistory):
        session.add(history)
        await session.merge(history)
        return history

import json
from datetime import date
from typing import List
from uuid import uuid4

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import String, Column, ForeignKey, Boolean, select, exists, Integer, DateTime, Enum, delete, and_, \
    desc, func, null
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload, backref
from sqlalchemy.dialects.postgresql import TEXT

from claon_admin.common.enum import PeriodType, MembershipType
from claon_admin.common.util.db import Base
from claon_admin.schema.post import Post


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


class ReviewTag:
    def __init__(self, word: str):
        self.word = word


class Center(Base):
    __tablename__ = 'tb_center'
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
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
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
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
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(length=10))
    difficulty = Column(String(length=10))
    is_color = Column(Boolean, default=False, nullable=False)

    center_id = Column(String(length=255), ForeignKey('tb_center.id', ondelete="CASCADE"), nullable=False)
    center = relationship("Center", back_populates="holds")


class CenterWall(Base):
    __tablename__ = 'tb_center_wall'
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(length=20))
    type = Column(String(length=20))

    center_id = Column(String(length=255), ForeignKey('tb_center.id', ondelete="CASCADE"), nullable=False)
    center = relationship("Center", back_populates="walls")


class CenterApprovedFile(Base):
    __tablename__ = 'tb_center_approved_file'
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    url = Column(String(length=255))

    user_id = Column(String(length=255), ForeignKey('tb_user.id', ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref=backref("CenterApprovedFile", passive_deletes=True))
    center_id = Column(String(length=255), ForeignKey('tb_center.id', ondelete="CASCADE"), nullable=False)
    center = relationship("Center", backref=backref("CenterApprovedFile", cascade="all,delete"))


class Review(Base):
    __tablename__ = "tb_review"
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    content = Column(String(length=500), nullable=False)
    created_at = Column(DateTime, nullable=False)
    _tag = Column(TEXT, nullable=False)

    user_id = Column(String(length=255), ForeignKey("tb_user.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref=backref("Review"))
    center_id = Column(String(length=255), ForeignKey("tb_center.id", ondelete="CASCADE"), nullable=False)
    center = relationship("Center", backref=backref("Review"))

    answer_id = Column(String(length=255), ForeignKey("tb_review_answer.id", ondelete="CASCADE"))
    answer = relationship("ReviewAnswer", back_populates="review")

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
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    content = Column(String(length=500), nullable=False)
    created_at = Column(DateTime, nullable=False)

    review = relationship("Review", back_populates="answer", uselist=False)


class CenterRepository:
    @staticmethod
    async def save(session: AsyncSession, center: Center):
        session.add(center)
        await session.merge(center)
        return center

    @staticmethod
    async def find_by_id(session: AsyncSession, center_id: str):
        result = await session.execute(select(Center).where(Center.id == center_id)
                                       .options(selectinload(Center.user))
                                       .options(selectinload(Center.holds))
                                       .options(selectinload(Center.walls)))
        return result.scalars().one_or_none()

    @staticmethod
    async def exists_by_id(session: AsyncSession, center_id: str):
        result = await session.execute(select(exists().where(Center.id == center_id)))
        return result.scalar()

    @staticmethod
    async def exists_by_name_and_approved(session: AsyncSession, name: str):
        result = await session.execute(select(exists().where(Center.name == name).where(Center.approved.is_(True))))
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
        result = await session.execute(select(Center).where(Center.approved.is_(False))
                                       .options(selectinload(Center.user))
                                       .options(selectinload(Center.holds))
                                       .options(selectinload(Center.walls))
                                       .options(selectinload(Center.fees)))
        return result.scalars().all()

    @staticmethod
    async def find_by_name(session:AsyncSession, name: str):
        result = await session.execute(select(Center)
                                       .where(and_(Center.name.contains(name), Center.user_id == null()))
                                       .limit(5))
        return result.scalars().all()

    @staticmethod
    async def find_all_by_user_id(session: AsyncSession, user_id: str, params: Params):
        query = select(Center).where(Center.user_id == user_id).options(selectinload(Center.user))
        return await paginate(query=query, conn=session, params=params)

    @staticmethod
    async def find_all_ids_by_approved_true(session: AsyncSession):
        result = await session.execute(select(Center.id).where(Center.approved.is_(True)))
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
                                     tag: str | None,
                                     is_answered: bool | None):
        query = select(Review, func.count(Post.id)) \
            .select_from(Review) \
            .join(Post, and_(Review.user_id == Post.user_id, Review.center_id == Post.center_id)) \
            .where(and_(Review.center_id == center_id,
                        Review.created_at >= start,
                        Review.created_at < end)) \
            .group_by(Review.id) \
            .order_by(desc(Review.created_at)) \
            .options(selectinload(Review.user)) \
            .options(selectinload(Review.center)) \
            .options(selectinload(Review.answer))

        if tag is not None:
            query = query.where(Review._tag.like(f'%{{"word": "{tag}"%'))

        if is_answered is not None:
            if is_answered is False:
                query = query.where(Review.answer == null())
            else:
                query = query.where(Review.answer != null())

        return await paginate(query=query, conn=session, params=params)

    @staticmethod
    async def find_by_id_and_center_id(session: AsyncSession,
                                       review_id: str,
                                       center_id: str):
        result = await session.execute(select(Review)
                                       .where(and_(Review.center_id == center_id, Review.id == review_id)))

        return result.scalars().one_or_none()

    @staticmethod
    async def find_all_by_center(session: AsyncSession, center_id: str):
        result = await session.execute(select(Review).where(Review.center_id == center_id))

        return result.scalars().all()


class ReviewAnswerRepository:
    @staticmethod
    async def save(session: AsyncSession, answer: ReviewAnswer):
        session.add(answer)
        await session.merge(answer)
        return answer

    @staticmethod
    async def update(session: AsyncSession, answer: ReviewAnswer, content: str):
        answer.content = content
        await session.merge(answer)
        return answer

    @staticmethod
    async def delete(session: AsyncSession, answer: ReviewAnswer):
        await session.delete(answer)

    @staticmethod
    async def find_by_review_id(session: AsyncSession, review_id: str):
        result = await session.execute(select(ReviewAnswer)
                                       .join(Review)
                                       .where(Review.id == review_id))

        return result.scalars().one_or_none()

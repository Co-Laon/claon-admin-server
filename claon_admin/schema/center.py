from datetime import date
from typing import List
from uuid import uuid4

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import String, Column, ForeignKey, Boolean, Integer, Enum, TEXT, JSON, \
    select, exists, delete, and_, desc, func, null, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload, backref

from claon_admin.common.enum import PeriodType, MembershipType
from claon_admin.common.util.db import Base, CastingArray
from claon_admin.common.util.repository import Repository
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

    _center_img = Column(CastingArray(JSON))
    _operating_time = Column(CastingArray(JSON))
    _utility = Column(CastingArray(JSON))
    _fee_img = Column(CastingArray(JSON))

    fees = relationship("CenterFee", back_populates="center", cascade="all, delete-orphan")
    holds = relationship("CenterHold", back_populates="center", cascade="all, delete-orphan")
    walls = relationship("CenterWall", back_populates="center", cascade="all, delete-orphan")

    user_id = Column(String(length=255), ForeignKey("tb_user.id", ondelete="SET NULL"))
    user = relationship("User", backref=backref("Center"))

    @property
    def center_img(self):
        if self._center_img is None:
            return []

        return [CenterImage(e['url']) for e in self._center_img]

    @center_img.setter
    def center_img(self, values: List[CenterImage]):
        self._center_img = [value.__dict__ for value in values]

    @property
    def operating_time(self):
        if self._operating_time is None:
            return []

        return [OperatingTime(e['day_of_week'], e['start_time'], e['end_time']) for e in self._operating_time]

    @operating_time.setter
    def operating_time(self, values: List[OperatingTime]):
        self._operating_time = [value.__dict__ for value in values]

    @property
    def utility(self):
        if self._utility is None:
            return []

        return [Utility(e['name']) for e in self._utility]

    @utility.setter
    def utility(self, values: List[Utility]):
        self._utility = [value.__dict__ for value in values]

    @property
    def fee_img(self):
        if self._fee_img is None:
            return []

        return [CenterFeeImage(e['url']) for e in self._fee_img]

    @fee_img.setter
    def fee_img(self, values: List[CenterFeeImage]):
        self._fee_img = [value.__dict__ for value in values]


class CenterFee(Base):
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
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(length=10))
    difficulty = Column(String(length=10))
    is_color = Column(Boolean, default=False, nullable=False)

    center_id = Column(String(length=255), ForeignKey('tb_center.id', ondelete="CASCADE"), nullable=False)
    center = relationship("Center", back_populates="holds")


class CenterWall(Base):
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(length=20))
    type = Column(String(length=20))

    center_id = Column(String(length=255), ForeignKey('tb_center.id', ondelete="CASCADE"), nullable=False)
    center = relationship("Center", back_populates="walls")


class CenterApprovedFile(Base):
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    url = Column(String(length=255))

    user_id = Column(String(length=255), ForeignKey('tb_user.id', ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref=backref("CenterApprovedFile", passive_deletes=True))
    center_id = Column(String(length=255), ForeignKey('tb_center.id', ondelete="CASCADE"), nullable=False)
    center = relationship("Center", backref=backref("CenterApprovedFile", cascade="all,delete"))


class Review(Base):
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    content = Column(String(length=500), nullable=False)
    _tag = Column(CastingArray(JSON), nullable=False)

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

        return [ReviewTag(t['word']) for t in self._tag]

    @tag.setter
    def tag(self, values: List[ReviewTag]):
        self._tag = [value.__dict__ for value in values]


class ReviewAnswer(Base):
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    content = Column(String(length=500), nullable=False)

    review = relationship("Review", back_populates="answer", uselist=False)


class CenterRepository(Repository[Center]):
    async def find_by_id_with_details(self, session: AsyncSession, center_id: str):
        result = await session.execute(select(Center).where(Center.id == center_id)
                                       .options(selectinload(Center.user))
                                       .options(selectinload(Center.holds))
                                       .options(selectinload(Center.walls))
                                       .options(selectinload(Center.fees)))
        return result.scalars().one_or_none()

    async def exists_by_name_and_approved(self, session: AsyncSession, name: str):
        result = await session.execute(select(exists().where(Center.name == name).where(Center.approved.is_(True))))
        return result.scalar()

    async def approve(self, session: AsyncSession, center: Center):
        center.approved = True
        await session.merge(center)
        return center

    async def find_all_by_approved_false(self, session: AsyncSession):
        result = await session.execute(select(Center).where(Center.approved.is_(False))
                                       .order_by(desc(Center.created_at))
                                       .options(selectinload(Center.user))
                                       .options(selectinload(Center.holds))
                                       .options(selectinload(Center.walls))
                                       .options(selectinload(Center.fees)))
        return result.scalars().all()

    async def find_by_name(self, session: AsyncSession, name: str):
        result = await session.execute(select(Center)
                                       .where(and_(Center.name.contains(name), Center.user_id == null()))
                                       .limit(5))
        return result.scalars().all()

    async def find_all_by_user_id(self, session: AsyncSession, user_id: str, params: Params):
        query = select(Center).where(Center.user_id == user_id) \
            .order_by(desc(Center.created_at)) \
            .options(selectinload(Center.user))
        return await paginate(query=query, conn=session, params=params)

    async def find_all_ids_by_approved_true(self, session: AsyncSession):
        result = await session.execute(select(Center.id).where(Center.approved.is_(True)))
        return result.scalars().all()

    async def remove_center(self, session: AsyncSession, center: Center):
        center.user_id = None
        await session.merge(center)
        return center


class CenterApprovedFileRepository(Repository[CenterApprovedFile]):
    async def find_all_by_center_id(self, session: AsyncSession, center_id: str):
        result = await session.execute(select(CenterApprovedFile).where(CenterApprovedFile.center_id == center_id))
        return result.scalars().all()

    async def delete_all_by_center_id(self, session: AsyncSession, center_id: str):
        await session.execute(delete(CenterApprovedFile).where(CenterApprovedFile.center_id == center_id))


class CenterHoldRepository(Repository[CenterHold]):
    async def find_all_by_center_id(self, session: AsyncSession, center_id: str):
        result = await session.execute(select(CenterHold).where(CenterHold.center_id == center_id))
        return result.scalars().all()


class CenterWallRepository(Repository[CenterWall]):
    async def find_all_by_center_id(self, session: AsyncSession, center_id: str):
        result = await session.execute(select(CenterWall).where(CenterWall.center_id == center_id))
        return result.scalars().all()


class CenterFeeRepository(Repository[CenterFee]):
    async def find_all_by_center_id(self, session: AsyncSession, center_id: str):
        result = await session.execute(select(CenterFee).where(CenterFee.center_id == center_id))
        return result.scalars().all()


class ReviewRepository(Repository[Review]):
    async def find_reviews_by_center(self,
                                     session: AsyncSession,
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
            tag_dict = [{"word": tag}]
            query = query.where(cast(Review._tag, CastingArray(JSON)).comparator.contains(tag_dict))

        if is_answered is not None:
            if is_answered is False:
                query = query.where(Review.answer == null())
            else:
                query = query.where(Review.answer != null())

        return await paginate(query=query, conn=session, params=params)

    async def find_by_id_and_center_id(self,
                                       session: AsyncSession,
                                       review_id: str,
                                       center_id: str):
        result = await session.execute(select(Review)
                                       .where(and_(Review.center_id == center_id, Review.id == review_id)))

        return result.scalars().one_or_none()

    async def find_all_by_center(self, session: AsyncSession, center_id: str):
        result = await session.execute(select(Review).where(Review.center_id == center_id))

        return result.scalars().all()


class ReviewAnswerRepository(Repository[ReviewAnswer]):
    async def update(self, session: AsyncSession, answer: ReviewAnswer, content: str):
        answer.content = content
        await session.merge(answer)
        return answer

    async def find_by_review_id(self, session: AsyncSession, review_id: str):
        result = await session.execute(select(ReviewAnswer)
                                       .join(Review)
                                       .where(Review.id == review_id))

        return result.scalars().one_or_none()

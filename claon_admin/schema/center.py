import json
from typing import List
from uuid import uuid4

from sqlalchemy import String, Column, ForeignKey, Boolean, select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload, backref
from sqlalchemy.dialects.postgresql import TEXT

from claon_admin.schema.conn import Base


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


class CenterFee:
    def __init__(self, name: str, price: int, count: int):
        self.name = name
        self.price = price
        self.count = count


class CenterFeeImage:
    def __init__(self, url: str):
        self.url = url


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
    _fee = Column(TEXT)
    _fee_img = Column(TEXT)

    holds = relationship("CenterHold", back_populates="center", cascade="all, delete-orphan")
    walls = relationship("CenterWall", back_populates="center", cascade="all, delete-orphan")

    user_id = Column(String(length=255), ForeignKey("tb_user.id"))
    user = relationship("User")

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
    def fee(self):
        if self._fee is None:
            return []

        values = json.loads(self._fee)
        return [CenterFee(value['name'], value['price'], value['count']) for value in values]

    @fee.setter
    def fee(self, values: List[CenterFee]):
        self._fee = json.dumps([value.__dict__ for value in values], default=str)

    @property
    def fee_img(self):
        if self._fee_img is None:
            return []

        data = json.loads(self._fee_img)
        return [CenterFeeImage(e['url']) for e in data]

    @fee_img.setter
    def fee_img(self, values: List[CenterFeeImage]):
        self._fee_img = json.dumps([value.__dict__ for value in values], default=str)


class CenterHold(Base):
    __tablename__ = 'tb_center_hold'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    name = Column(String(length=10))
    difficulty = Column(String(length=10))
    is_color = Column(Boolean, default=False, nullable=False)

    center_id = Column(String(length=255), ForeignKey('tb_center.id'), nullable=False)
    center = relationship("Center", back_populates="holds")


class CenterWall(Base):
    __tablename__ = 'tb_center_wall'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    name = Column(String(length=20))
    type = Column(String(length=20))

    center_id = Column(String(length=255), ForeignKey('tb_center.id'), nullable=False)
    center = relationship("Center", back_populates="walls")


class CenterApprovedFile(Base):
    __tablename__ = 'tb_center_approved_file'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    url = Column(String(length=255))

    user_id = Column(String(length=255), ForeignKey('tb_user.id'), nullable=False)
    user = relationship("User")
    center_id = Column(String(length=255), ForeignKey('tb_center.id'), nullable=False)
    center = relationship("Center", backref=backref("CenterApprovedFile", cascade="all, delete"))


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
        result = await session.execute(select(CenterApprovedFile).where(CenterApprovedFile.center_id == center_id))
        [await session.delete(e) for e in result.scalars().all()]


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

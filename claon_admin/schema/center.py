import json
from uuid import uuid4

from sqlalchemy import String, Column, ForeignKey, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, backref

from claon_admin.schema.conn import Base
from claon_admin.schema.user import User


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
    def __init__(self, price: int, count: int):
        self.price = price
        self.count = count


class CenterFeeImage:
    def __init__(self, url: str):
        self.url = url


class Center(Base):
    __tablename__ = 'tb_center'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    user_id = Column(String(length=255), ForeignKey("tb_user.id"))
    user = relationship("User", backref=backref("centers"))
    name = Column(String(length=30), nullable=False)
    profile_img = Column(String(255), nullable=False)
    address = Column(String(length=255), nullable=False)
    detail_address = Column(String(length=255))
    tel = Column(String(length=255), nullable=False)
    web_url = Column(String(length=500))
    instagram_name = Column(String())
    youtube_url = Column(String(length=500))
    _center_img = Column(String(length=255))
    _operating_time = Column(String(length=255))
    _utility = Column(String(length=255))
    _fee = Column(String(length=255))
    _fee_img = Column(String(length=255))
    holds = relationship("CenterHold", back_populates="center")
    walls = relationship("CenterWall", back_populates="center")
    approved_files = relationship("CenterApprovedFile", back_populates="center")
    approved = Column(Boolean, default=False, nullable=False)

    @property
    def center_img(self):
        data = json.loads(self._center_img)
        return CenterImage(data['url'])

    @center_img.setter
    def center_img(self, value: CenterImage):
        self._center_img = json.dumps(value.__dict__)

    @property
    def operating_time(self):
        data = json.loads(self._operating_time)
        return OperatingTime(data['day_of_week'], data['start_time'], data['end_time'])

    @operating_time.setter
    def operating_time(self, value: OperatingTime):
        self._operating_time = json.dumps(value.__dict__)

    @property
    def utility(self):
        data = json.loads(self._utility)
        return Utility(data['name'])

    @utility.setter
    def utility(self, value: Utility):
        self._utility = json.dumps(value.__dict__)

    @property
    def fee(self):
        data = json.loads(self._fee)
        return CenterFee(data['price'], data['count'])

    @fee.setter
    def fee(self, value: CenterFee):
        self._fee = json.dumps(value.__dict__)

    @property
    def fee_img(self):
        data = json.loads(self._fee_img)
        return CenterFeeImage(data['url'])

    @fee_img.setter
    def fee_img(self, value: CenterFeeImage):
        self._fee_img = json.dumps(value.__dict__)


class CenterHold(Base):
    __tablename__ = 'tb_center_hold'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    center_id = Column(String(length=255), ForeignKey('tb_center.id'))
    center = relationship("Center", back_populates="holds")
    name = Column(String(length=10))
    color = Column(String())


class CenterWall(Base):
    __tablename__ = 'tb_center_wall'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    center_id = Column(String(length=255), ForeignKey('tb_center.id'))
    center = relationship("Center", back_populates="walls")
    name = Column(String(length=20))
    type = Column(String(length=20))


class CenterApprovedFile(Base):
    __tablename__ = 'tb_center_approved_file'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    center_id = Column(String(length=255), ForeignKey('tb_center.id'))
    center = relationship("Center", back_populates="approved_files")
    url = Column(String(length=255))


class CenterRepository:

    @staticmethod
    async def save(session: AsyncSession, center: Center):
        session.add(center)
        await session.flush()
        return center

import json
from datetime import date
from typing import List
from uuid import uuid4

from sqlalchemy import Column, String, Enum, Boolean, ForeignKey, select, exists, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TEXT

from claon_admin.model.enum import Role
from claon_admin.schema.conn import Base


class Contest:
    def __init__(self, year: int, title: str, name: str):
        self.year = year
        self.title = title
        self.name = name


class Certificate:
    def __init__(self, acquisition_date: date, rate: int, name: str):
        self.acquisition_date = acquisition_date
        self.rate = rate
        self.name = name


class Career:
    def __init__(self, start_date: date, end_date: date, name: str):
        self.start_date = start_date
        self.end_date = end_date
        self.name = name


class User(Base):
    __tablename__ = 'tb_user'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    oauth_id = Column(String(length=255), nullable=False)
    nickname = Column(String(length=40), nullable=False, unique=True)
    profile_img = Column(TEXT, nullable=False)
    sns = Column(String(length=500), nullable=False, unique=True)
    email = Column(String(length=500), unique=True)
    instagram_name = Column(String(length=255), unique=True)
    role = Column(Enum(Role), nullable=False)

    def is_signed_up(self):
        if self.role == Role.PENDING:
            return False
        else:
            return True


class Lector(Base):
    __tablename__ = 'tb_lector'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    is_setter = Column(Boolean, default=False, nullable=False)
    approved = Column(Boolean, default=False, nullable=False)

    _contest = Column(TEXT)
    _certificate = Column(TEXT)
    _career = Column(TEXT)

    user_id = Column(String(length=255), ForeignKey("tb_user.id"), unique=True, nullable=False)
    user = relationship("User")

    @property
    def contest(self):
        values = json.loads(self._contest)
        return [Contest(value['year'], value['title'], value['name']) for value in values]

    @contest.setter
    def contest(self, values: List[Contest]):
        self._contest = json.dumps([value.__dict__ for value in values], default=str)

    @property
    def certificate(self):
        values = json.loads(self._certificate)
        return [Certificate(value['acquisition_date'], value['rate'], value['name']) for value in values]

    @certificate.setter
    def certificate(self, values: List[Certificate]):
        self._certificate = json.dumps([value.__dict__ for value in values], default=str)

    @property
    def career(self):
        values = json.loads(self._career)
        return [Career(value['start_date'], value['end_date'], value['name']) for value in values]

    @career.setter
    def career(self, values: List[Career]):
        self._career = json.dumps([value.__dict__ for value in values], default=str)


class LectorApprovedFile(Base):
    __tablename__ = 'tb_lector_approved_file'
    id = Column(String(length=255), primary_key=True, default=str(uuid4()))
    url = Column(String(length=255))

    lector_id = Column(String(length=255), ForeignKey('tb_lector.id'))
    lector = relationship("Lector")


class UserRepository:
    @staticmethod
    async def find_by_id(session: AsyncSession, user_id: str):
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalars().one_or_none()

    @staticmethod
    async def find_by_nickname(session: AsyncSession, nickname: str):
        result = await session.execute(select(User).where(User.nickname == nickname))
        return result.scalars().one_or_none()

    @staticmethod
    async def exist_by_id(session: AsyncSession, user_id: str):
        result = await session.execute(select(exists().where(User.id == user_id)))
        return result.scalar()

    @staticmethod
    async def exist_by_nickname(session: AsyncSession, nickname: str):
        result = await session.execute(select(exists().where(User.nickname == nickname)))
        return result.scalar()

    @staticmethod
    async def save(session: AsyncSession, user: User):
        session.add(user)
        await session.flush()
        return user

    @staticmethod
    async def find_by_oauth_id_and_sns(session: AsyncSession, oauth_id: str, sns: str):
        result = await session.execute(select(User).where(and_(User.oauth_id == oauth_id, User.sns == sns)))
        return result.scalars().one_or_none()


class LectorRepository:
    @staticmethod
    async def save(session: AsyncSession, lector: Lector):
        session.add(lector)
        await session.flush()
        return lector


class LectorApprovedFileRepository:
    @staticmethod
    async def save(session: AsyncSession, approved_file: LectorApprovedFile):
        session.add(approved_file)
        await session.flush()
        return approved_file

    @staticmethod
    async def save_all(session: AsyncSession, approved_files: List[LectorApprovedFile]):
        session.add_all(approved_files)
        await session.flush()
        return approved_files

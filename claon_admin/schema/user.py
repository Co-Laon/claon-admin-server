import json
from datetime import date
from typing import List
from uuid import uuid4

from sqlalchemy import Column, String, Enum, Boolean, ForeignKey, select, exists, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, backref, selectinload
from sqlalchemy.dialects.postgresql import TEXT

from claon_admin.common.enum import Role
from claon_admin.common.util.db import Base


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
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    oauth_id = Column(String(length=255), nullable=False, unique=True)
    nickname = Column(String(length=40), nullable=False, unique=True)
    profile_img = Column(TEXT, nullable=False)
    sns = Column(String(length=500), nullable=False)
    email = Column(String(length=500))
    instagram_name = Column(String(length=255), unique=True)
    role = Column(Enum(Role), nullable=False)

    def is_signed_up(self):
        if self.role == Role.PENDING:
            return False
        else:
            return True


class Lector(Base):
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    is_setter = Column(Boolean, default=False, nullable=False)
    approved = Column(Boolean, default=False, nullable=False)

    _contest = Column(TEXT)
    _certificate = Column(TEXT)
    _career = Column(TEXT)

    user_id = Column(String(length=255), ForeignKey("tb_user.id", ondelete="CASCADE"), unique=True, nullable=False)
    user = relationship("User", backref=backref("Lector"))

    @property
    def contest(self):
        if self._contest is None:
            return []

        values = json.loads(self._contest)
        return [Contest(value['year'], value['title'], value['name']) for value in values]

    @contest.setter
    def contest(self, values: List[Contest]):
        self._contest = json.dumps([value.__dict__ for value in values], default=str)

    @property
    def certificate(self):
        if self._certificate is None:
            return []

        values = json.loads(self._certificate)
        return [Certificate(value['acquisition_date'], value['rate'], value['name']) for value in values]

    @certificate.setter
    def certificate(self, values: List[Certificate]):
        self._certificate = json.dumps([value.__dict__ for value in values], default=str)

    @property
    def career(self):
        if self._career is None:
            return []

        values = json.loads(self._career)
        return [Career(value['start_date'], value['end_date'], value['name']) for value in values]

    @career.setter
    def career(self, values: List[Career]):
        self._career = json.dumps([value.__dict__ for value in values], default=str)


class LectorApprovedFile(Base):
    id = Column(String(length=255), primary_key=True, default=lambda: str(uuid4()))
    url = Column(String(length=255))

    lector_id = Column(String(length=255), ForeignKey('tb_lector.id', ondelete="CASCADE"), nullable=False)
    lector = relationship("Lector", backref=backref("LectorApprovedFile", cascade="all,delete"))


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
        await session.merge(user)
        return user

    @staticmethod
    async def find_by_oauth_id_and_sns(session: AsyncSession, oauth_id: str, sns: str):
        result = await session.execute(select(User).where(and_(User.oauth_id == oauth_id, User.sns == sns)))
        return result.scalars().one_or_none()

    @staticmethod
    async def find_by_oauth_id(session: AsyncSession, oauth_id: str):
        result = await session.execute(select(User).where(User.oauth_id == oauth_id))
        return result.scalars().one_or_none()

    @staticmethod
    async def update_role(session: AsyncSession, user: User, role: Role):
        user.role = role
        await session.merge(user)
        return user


class LectorRepository:
    @staticmethod
    async def save(session: AsyncSession, lector: Lector):
        session.add(lector)
        await session.merge(lector)
        return lector

    @staticmethod
    async def delete(session: AsyncSession, lector: Lector):
        await session.delete(lector)

    @staticmethod
    async def find_by_id(session: AsyncSession, lector_id: str):
        result = await session.execute(select(Lector).where(Lector.id == lector_id))
        return result.scalars().one_or_none()

    @staticmethod
    async def exists_by_id(session: AsyncSession, lector_id: str):
        result = await session.execute(select(exists().where(Lector.id == lector_id)))
        return result.scalar()

    @staticmethod
    async def approve(session: AsyncSession, lector: Lector):
        lector.approved = True
        await session.merge(lector)
        return lector

    @staticmethod
    async def find_all_by_approved_false(session: AsyncSession):
        result = await session.execute(
            select(Lector)
            .where(Lector.approved.is_(False))
            .options(selectinload(Lector.user))
        )

        return result.scalars().all()


class LectorApprovedFileRepository:
    @staticmethod
    async def save(session: AsyncSession, approved_file: LectorApprovedFile):
        session.add(approved_file)
        await session.merge(approved_file)
        return approved_file

    @staticmethod
    async def save_all(session: AsyncSession, approved_files: List[LectorApprovedFile]):
        session.add_all(approved_files)
        [await session.merge(e) for e in approved_files]
        return approved_files

    @staticmethod
    async def find_all_by_lector_id(session: AsyncSession, lector_id: str):
        result = await session.execute(select(LectorApprovedFile).where(LectorApprovedFile.lector_id == lector_id))
        return result.scalars().all()

    @staticmethod
    async def delete_all_by_lector_id(session: AsyncSession, lector_id: str):
        await session.execute(delete(LectorApprovedFile).where(LectorApprovedFile.lector_id == lector_id))

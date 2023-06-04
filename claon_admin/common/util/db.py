from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base, declared_attr

from claon_admin.common.util.time import now
from claon_admin.config.config import conf


class DeclarativeBase(object):
    @declared_attr
    def __tablename__(cls):
        return "tb_" + \
            "".join(['_' + i.lower() if i.isupper() else i for i in getattr(cls, "__name__")]).lstrip("_")

    @declared_attr
    def created_at(cls):
        return Column(DateTime, nullable=False, default=now())


Base = declarative_base(cls=DeclarativeBase)


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine: AsyncEngine = create_async_engine(db_url, echo=True, pool_pre_ping=True)
        self.async_session_maker = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            if conf().DB_DDL_AUTO == "create":
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            elif conf().DB_DDL_AUTO == "none":
                await conn.run_sync(Base.metadata.create_all)
            else:
                await conn.run_sync(Base.metadata.create_all)


db = Database(db_url=conf().DB_URL)

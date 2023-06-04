from claon_admin.common.util.db import db


async def __read_only_transactional(self, func, args, kwargs):
    async with db.async_session_maker() as session:
        try:
            result = await func(self, session, *args, **kwargs)
            return result
        finally:
            await session.close()


async def __transactional(self, func, args, kwargs):
    async with db.async_session_maker() as session:
        try:
            result = await func(self, session, *args, **kwargs)
            await session.commit()
            return result
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


def transactional(read_only: bool = False):
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            if read_only:
                return await __read_only_transactional(self, func, args, kwargs)
            else:
                return await __transactional(self, func, args, kwargs)

        return wrapper

    return decorator

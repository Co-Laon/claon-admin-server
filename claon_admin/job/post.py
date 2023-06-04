from datetime import timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dependency_injector.wiring import inject, Provide

from claon_admin.common.util.db import db
from claon_admin.common.util.time import now
from claon_admin.container import Container
from claon_admin.schema.center import CenterRepository
from claon_admin.schema.post import PostRepository, PostCountHistoryRepository, PostCountHistory

scheduler = AsyncIOScheduler()


@inject
async def count_post_by_day(
        center_repository: CenterRepository = Provide[Container.center_repository],
        post_repository: PostRepository = Provide[Container.post_repository],
        post_count_history_repository: PostCountHistoryRepository = Provide[Container.post_count_history_repository]
):
    async with db.async_session_maker() as session:
        center_ids = await center_repository.find_all_ids_by_approved_true(session)

        end_date = now().date()
        start_date = end_date - timedelta(days=1)
        post_count_by_center = await post_repository.count_by_center_and_date(session, center_ids, start_date, end_date)

        await post_count_history_repository.save_all(session, [PostCountHistory(
            center_id=center_id,
            count=count,
            reg_date=start_date
        ) for center_id, count in post_count_by_center])


def add_job():
    scheduler.add_job(count_post_by_day, "cron", hour=0, minute=0, second=0)


def start():
    add_job()
    scheduler.start()


def shutdown():
    scheduler.shutdown()

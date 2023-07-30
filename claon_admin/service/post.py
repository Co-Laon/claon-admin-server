from datetime import timedelta

from fastapi_pagination import Params
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.common.util.pagination import paginate
from claon_admin.common.util.time import now
from claon_admin.common.util.transaction import transactional
from claon_admin.model.auth import RequestUser
from claon_admin.model.post import PostSummaryResponseDto, PostBriefResponseDto, PostFinder
from claon_admin.schema.center import CenterRepository
from claon_admin.schema.post import PostCountHistoryRepository, PostRepository


class PostService:
    def __init__(self,
                 center_repository: CenterRepository,
                 post_repository: PostRepository,
                 post_count_history_repository: PostCountHistoryRepository):
        self.center_repository = center_repository
        self.post_repository = post_repository
        self.post_count_history_repository = post_count_history_repository

    @transactional(read_only=True)
    async def find_posts_summary_by_center(self,
                                           session: AsyncSession,
                                           subject: RequestUser,
                                           center_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if not center.is_owner(subject.id):
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        total_count = await self.post_count_history_repository.sum_count_by_center(session, center.id)

        end_date = now().date()
        start_date = end_date - timedelta(days=52 * 7 + end_date.weekday())
        count_history_by_year = await self.post_count_history_repository.find_by_center_and_date(
            session,
            center.id,
            start_date,
            end_date
        )

        return PostSummaryResponseDto.from_entity(center, end_date, total_count, count_history_by_year)

    @transactional(read_only=True)
    async def find_posts_by_center(self,
                                   session: AsyncSession,
                                   subject: RequestUser,
                                   params: Params,
                                   center_id: str,
                                   finder: PostFinder):
        center = await self.center_repository.find_by_id_with_details(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if not center.is_owner(subject.id):
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        if finder.hold_id is not None and not center.exist_hold(finder.hold_id):
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 홀드가 암장에 존재하지 않습니다."
            )

        pages = await self.post_repository.find_posts_by_center(
            session,
            params,
            center_id,
            finder.hold_id,
            finder.start_date,
            finder.end_date
        )

        return await paginate(PostBriefResponseDto, pages)

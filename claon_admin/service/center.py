from datetime import date, datetime
from typing import Optional

from fastapi_pagination import Params
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import BadRequestException, ErrorCode, UnauthorizedException, NotFoundException
from claon_admin.common.util.pagination import PaginationFactory
from claon_admin.config.consts import TIME_ZONE_KST
from claon_admin.model.post import PostBriefResponseDto, PostSummaryResponseDto, PostCount
from claon_admin.model.review import ReviewBriefResponseDto, ReviewAnswerRequestDto, ReviewAnswerResponseDto
from claon_admin.schema.center import PostRepository, CenterRepository, ReviewRepository, ReviewAnswerRepository, \
    ReviewAnswer


class CenterService:
    def __init__(self,
                 center_repository: CenterRepository,
                 post_repository: PostRepository,
                 review_repository: ReviewRepository,
                 review_answer_repository: ReviewAnswerRepository,
                 pagination_factory: PaginationFactory):
        self.center_repository = center_repository
        self.post_repository = post_repository
        self.review_repository = review_repository
        self.review_answer_repository = review_answer_repository
        self.pagination_factory = pagination_factory

    async def find_posts_by_center(self,
                                   session: AsyncSession,
                                   params: Params,
                                   center_id: str,
                                   hold_id: Optional[str],
                                   start: date,
                                   end: date):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.role != Role.CENTER_ADMIN:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        if hold_id is not None:
            hold_ids = [h.id for h in center.holds]
            if hold_id not in hold_ids:
                raise NotFoundException(
                    ErrorCode.DATA_DOES_NOT_EXIST,
                    "해당 홀드가 암장에 존재하지 않습니다."
                )

        pages = await self.post_repository.find_posts_by_center(
            session=session,
            params=params,
            center_id=center_id,
            hold_id=hold_id,
            start=start,
            end=end
        )

        return await self.pagination_factory.create(PostBriefResponseDto, pages)

    async def find_reviews_by_center(self,
                                     session: AsyncSession,
                                     params: Params,
                                     center_id: str,
                                     start: date,
                                     end: date,
                                     tag: Optional[str],
                                     is_answered: Optional[bool]):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if (end - start).days > 365 or (end - start).days < 0:
            raise BadRequestException(
                ErrorCode.WRONG_DATE_RANGE,
                "잘못된 날짜 범위입니다."
            )

        if center.user.role != Role.CENTER_ADMIN:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        pages = await self.review_repository.find_reviews_by_center(
            session=session,
            params=params,
            center_id=center_id,
            start=start,
            end=end,
            tag=tag,
            is_answered=is_answered
        )

        return await self.pagination_factory.create(ReviewBriefResponseDto, pages)

    async def create_review_answer(self,
                                   session: AsyncSession,
                                   dto: ReviewAnswerRequestDto,
                                   center_id: str,
                                   review_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.role != Role.CENTER_ADMIN:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        review = await self.review_repository.find_by_id_and_center_id(session, review_id, center.id)
        if review is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 리뷰가 암장에 존재하지 않습니다."
            )

        answer = await self.review_answer_repository.find_by_review_id(session, review.id)
        if answer is not None:
            raise NotFoundException(
                ErrorCode.ROW_ALREADY_EXIST,
                "이미 작성된 답변이 존재합니다."
            )

        new_answer = ReviewAnswer(
            content=dto.answer_content,
            created_at=datetime.now(TIME_ZONE_KST),
            review=review
        )

        result = await self.review_answer_repository.save(session, new_answer)

        return ReviewAnswerResponseDto.from_entity(result)

    async def update_review_answer(self,
                                   session: AsyncSession,
                                   dto: ReviewAnswerRequestDto,
                                   center_id: str,
                                   review_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.role != Role.CENTER_ADMIN:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        review = await self.review_repository.find_by_id_and_center_id(session, review_id, center.id)
        if review is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "암장에 해당 리뷰가 존재하지 않습니다."
            )

        answer = await self.review_answer_repository.find_by_review_id(session, review.id)
        if answer is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 리뷰에 답변이 존재하지 않습니다."
            )

        result = await self.review_answer_repository.update(session, answer, dto.answer_content)

        return ReviewAnswerResponseDto.from_entity(result)

    async def delete_review_answer(self,
                                   session: AsyncSession,
                                   center_id: str,
                                   review_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.role != Role.CENTER_ADMIN:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        review = await self.review_repository.find_by_id_and_center_id(session, review_id, center.id)
        if review is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "암장에 해당 리뷰가 존재하지 않습니다."
            )

        answer = await self.review_answer_repository.find_by_review_id(session, review.id)
        if answer is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 리뷰에 답변이 존재하지 않습니다."
            )

        return await self.review_answer_repository.delete(session, answer)

    async def find_posts_summary_by_center(self,
                                           session: AsyncSession,
                                           center_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.role != Role.CENTER_ADMIN:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        counts = await self.post_repository.find_posts_summary_by_center(session, center.id)

        standard_year = datetime.now(TIME_ZONE_KST).isocalendar()[0]
        standard_week = datetime.now(TIME_ZONE_KST).isocalendar()[1]
        standard_day = datetime.now(TIME_ZONE_KST).isocalendar()[2]

        weeks_posts = counts[4]
        count_per_day = [PostCount(unit=f"{7 - day - 1}일 전", count=0) for day in range(0, 7)]
        for w_post in weeks_posts:
            created_at: datetime = w_post[1]
            week = created_at.isocalendar()[1]
            day = created_at.isocalendar()[2]
            if week == standard_week:
                count_per_day[day + (7 - standard_day - 1)].count += 1
            else:
                count_per_day[day - standard_day - 1].count += 1

        counts[4] = count_per_day

        years_posts = counts[5]
        count_per_week = [PostCount(unit=f"{52 - week - 1}주 전", count=0) for week in range(0, 52)]

        for post in years_posts:
            created_at: datetime = post[1]
            year = created_at.isocalendar()[0]
            week = created_at.isocalendar()[1]
            if year == standard_year:
                count_per_week[week + (52 - standard_week - 1)].count += 1
            else:
                count_per_week[week - standard_week - 1].count += 1

        counts[5] = count_per_week

        return PostSummaryResponseDto.from_entity(center.id, center.name, counts)

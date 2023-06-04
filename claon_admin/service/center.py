from collections import Counter
from datetime import date, timedelta

from fastapi import UploadFile
from fastapi_pagination import Params
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import CenterUploadPurpose, Role
from claon_admin.common.error.exception import BadRequestException, ErrorCode, UnauthorizedException, NotFoundException, ConflictException
from claon_admin.common.util.pagination import paginate
from claon_admin.common.util.s3 import upload_file
from claon_admin.common.util.time import now
from claon_admin.common.util.transaction import transactional
from claon_admin.model.auth import RequestUser
from claon_admin.model.file import UploadFileResponseDto
from claon_admin.model.post import PostBriefResponseDto, PostSummaryResponseDto
from claon_admin.model.review import ReviewBriefResponseDto, ReviewAnswerRequestDto, ReviewAnswerResponseDto, \
    ReviewTagDto, ReviewSummaryResponseDto
from claon_admin.model.center import CenterNameResponseDto, CenterBriefResponseDto, CenterResponseDto
from claon_admin.schema.center import CenterRepository, ReviewRepository, ReviewAnswerRepository, ReviewAnswer
from claon_admin.schema.post import PostRepository, PostCountHistoryRepository


class CenterService:
    def __init__(self,
                 center_repository: CenterRepository,
                 post_repository: PostRepository,
                 post_count_history_repository: PostCountHistoryRepository,
                 review_repository: ReviewRepository,
                 review_answer_repository: ReviewAnswerRepository):
        self.center_repository = center_repository
        self.post_repository = post_repository
        self.post_count_history_repository = post_count_history_repository
        self.review_repository = review_repository
        self.review_answer_repository = review_answer_repository

    @transactional(read_only=True)
    async def find_posts_by_center(self,
                                   session: AsyncSession,
                                   subject: RequestUser,
                                   params: Params,
                                   center_id: str,
                                   hold_id: str | None,
                                   start: date,
                                   end: date):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.id != subject.id:
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

        return await paginate(PostBriefResponseDto, pages)

    @transactional(read_only=True)
    async def find_reviews_by_center(self,
                                     session: AsyncSession,
                                     subject: RequestUser,
                                     params: Params,
                                     center_id: str,
                                     start: date,
                                     end: date,
                                     tag: str | None,
                                     is_answered: bool | None):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.id != subject.id:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        if (end - start).days > 365 or (end - start).days < 0:
            raise BadRequestException(
                ErrorCode.WRONG_DATE_RANGE,
                "잘못된 날짜 범위입니다."
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

        return await paginate(ReviewBriefResponseDto, pages)

    @transactional()
    async def create_review_answer(self,
                                   session: AsyncSession,
                                   subject: RequestUser,
                                   dto: ReviewAnswerRequestDto,
                                   center_id: str,
                                   review_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.id != subject.id:
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
            review=review
        )

        result = await self.review_answer_repository.save(session, new_answer)

        return ReviewAnswerResponseDto.from_entity(result)

    @transactional()
    async def update_review_answer(self,
                                   session: AsyncSession,
                                   subject: RequestUser,
                                   dto: ReviewAnswerRequestDto,
                                   center_id: str,
                                   review_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.id != subject.id:
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

    @transactional()
    async def delete_review_answer(self,
                                   session: AsyncSession,
                                   subject: RequestUser,
                                   center_id: str,
                                   review_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.id != subject.id:
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

    async def upload_file(self, purpose: CenterUploadPurpose, file: UploadFile):
        if file.filename.split('.')[-1] not in CenterUploadPurpose.get_extensions(purpose.value):
            raise BadRequestException(
                ErrorCode.INVALID_FORMAT,
                "지원하지 않는 포맷입니다."
            )

        url = await upload_file(file=file, domain="center", purpose=purpose.value)
        return UploadFileResponseDto(file_url=url)

    @transactional(read_only=True)
    async def find_centers_by_name(self,
                                   session: AsyncSession,
                                   name: str):
        centers = await self.center_repository.find_by_name(session, name)
        return [CenterNameResponseDto.from_entity(center) for center in centers]

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

        if center.user.id != subject.id:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        total_count = await self.post_count_history_repository.sum_count_by_center(session, center.id)

        end_date = now().date()
        start_date = end_date - timedelta(days=52 * 7 + end_date.weekday())
        count_history_by_year = await self.post_count_history_repository.find_by_center_and_date(session,
                                                                                                 center.id,
                                                                                                 start_date,
                                                                                                 end_date)

        return PostSummaryResponseDto.from_entity(
            center,
            end_date,
            total_count,
            count_history_by_year
        )

    @transactional(read_only=True)
    async def find_centers(self,
                           session: AsyncSession,
                           params: Params,
                           subject: RequestUser):
        if subject.role != Role.CENTER_ADMIN:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        pages = await self.center_repository.find_all_by_user_id(session, subject.id, params)

        if not pages.items:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "등록된 암장이 존재하지 않습니다."
            )

        return await paginate(CenterBriefResponseDto, pages)

    @transactional(read_only=True)
    async def find_reviews_summary_by_center(self,
                                             session: AsyncSession,
                                             subject: RequestUser,
                                             center_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.id != subject.id:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        reviews = await self.review_repository.find_all_by_center(session, center.id)

        is_answer, tags = [], []
        for review in reviews:
            is_answer.append(False if review.answer_id is None else True)
            tags.append(review.tag)

        tag_list = [t.word for t in sum(tags, [])]

        return ReviewSummaryResponseDto.from_entity(
            center,
            Counter(is_answer),
            [ReviewTagDto(tag=tag, count=count) for tag, count in Counter(tag_list).items()]
        )

    @transactional(read_only=True)
    async def find_by_id(self,
                         session: AsyncSession,
                         subject: RequestUser,
                         center_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user.id != subject.id:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        return CenterResponseDto.from_entity(center, center.holds, center.walls, center.fees)

    async def delete(self,
                     session: AsyncSession,
                     subject: RequestUser,
                     center_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user_id is None:
            raise ConflictException(
                ErrorCode.CONFLICT_STATE,
                "이미 삭제된 암장입니다."
            )

        if center.user.id != subject.id:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        result = await self.center_repository.remove_center(session, center)
        return CenterResponseDto.from_entity(result, result.holds, result.walls, result.fees)

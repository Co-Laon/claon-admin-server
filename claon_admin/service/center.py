from datetime import date, datetime
from typing import Optional

from fastapi import UploadFile
from fastapi_pagination import Params
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import Role, CenterUploadPurpose
from claon_admin.common.error.exception import BadRequestException, ErrorCode, UnauthorizedException, NotFoundException
from claon_admin.common.util.pagination import PaginationFactory
from claon_admin.common.util.s3 import upload_file
from claon_admin.config.consts import TIME_ZONE_KST
from claon_admin.model.file import UploadFileResponseDto
from claon_admin.model.post import PostBriefResponseDto
from claon_admin.model.review import ReviewBriefResponseDto, ReviewAnswerRequestDto, ReviewAnswerResponseDto
from claon_admin.model.center import CenterNameResponseDto
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

    async def upload_file(self, purpose: CenterUploadPurpose, file: UploadFile):
        if file.filename.split('.')[-1] not in CenterUploadPurpose.get_extensions(purpose.value):
            raise BadRequestException(
                ErrorCode.INVALID_FORMAT,
                "지원하지 않는 포맷입니다."
            )

        url = await upload_file(file=file, domain="center", purpose=purpose.value)
        return UploadFileResponseDto(file_url=url)

    async def find_center_by_name(self,
                                  session: AsyncSession,
                                  name: str):
        center = await self.center_repository.find_by_name(session, name)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )
        return CenterNameResponseDto.from_entity(center)

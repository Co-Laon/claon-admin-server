from collections import Counter

from fastapi_pagination import Params
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.common.util.pagination import paginate
from claon_admin.common.util.transaction import transactional
from claon_admin.model.auth import RequestUser
from claon_admin.model.review import ReviewBriefResponseDto, ReviewAnswerRequestDto, ReviewAnswerResponseDto, \
    ReviewSummaryResponseDto, ReviewTagDto, ReviewFinder
from claon_admin.schema.center import CenterRepository, ReviewRepository, ReviewAnswerRepository, ReviewAnswer


class ReviewService:
    def __init__(self,
                 center_repository: CenterRepository,
                 review_repository: ReviewRepository,
                 review_answer_repository: ReviewAnswerRepository):
        self.center_repository = center_repository
        self.review_repository = review_repository
        self.review_answer_repository = review_answer_repository

    @transactional(read_only=True)
    async def find_reviews_by_center(self,
                                     session: AsyncSession,
                                     subject: RequestUser,
                                     params: Params,
                                     center_id: str,
                                     finder: ReviewFinder):
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

        pages = await self.review_repository.find_reviews_by_center(
            session,
            params,
            center_id,
            finder.start_date,
            finder.end_date,
            finder.tag,
            finder.is_answered
        )

        return await paginate(ReviewBriefResponseDto, pages)

    @transactional()
    async def create_review_answer(self,
                                   session: AsyncSession,
                                   subject: RequestUser,
                                   center_id: str,
                                   review_id: str,
                                   req: ReviewAnswerRequestDto):
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

        review = await self.review_repository.find_by_id_and_center_id(session, review_id, center.id)
        if review is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 리뷰가 암장에 존재하지 않습니다."
            )

        if review.answer is not None:
            raise NotFoundException(
                ErrorCode.ROW_ALREADY_EXIST,
                "이미 작성된 답변이 존재합니다."
            )

        new_answer = ReviewAnswer(
            content=req.answer_content,
            review=review
        )

        result = await self.review_answer_repository.save(session, new_answer)

        return ReviewAnswerResponseDto.from_entity(result)

    @transactional()
    async def update_review_answer(self,
                                   session: AsyncSession,
                                   subject: RequestUser,
                                   center_id: str,
                                   review_id: str,
                                   req: ReviewAnswerRequestDto):
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

        review = await self.review_repository.find_by_id_and_center_id(session, review_id, center.id)
        if review is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "암장에 해당 리뷰가 존재하지 않습니다."
            )

        if review.answer is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 리뷰에 답변이 존재하지 않습니다."
            )

        review.answer.update(req.answer_content)

        return ReviewAnswerResponseDto.from_entity(review.answer)

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

        if not center.is_owner(subject.id):
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

        if review.answer is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 리뷰에 답변이 존재하지 않습니다."
            )

        return await self.review_answer_repository.delete(session, review.answer)

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

        if not center.is_owner(subject.id):
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

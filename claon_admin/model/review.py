from typing import List, Optional, Tuple

from pydantic import BaseModel, validator

from claon_admin.common.util.time import get_relative_time
from claon_admin.schema.center import Review, ReviewAnswer


class ReviewAnswerRequestDto(BaseModel):
    answer_content: str

    @validator('answer_content')
    def validate_name(cls, value):
        if len(value) > 500:
            raise ValueError('답글은 500자 이하로 입력해 주세요.')
        return value


class ReviewAnswerResponseDto(BaseModel):
    review_answer_id: str
    content: str
    created_at: str
    review_id: str

    @classmethod
    def from_entity(cls, entity: ReviewAnswer):
        return ReviewAnswerResponseDto(
            review_answer_id=entity.id,
            content=entity.content,
            created_at=get_relative_time(entity.created_at),
            review_id=entity.review.id
        )


class ReviewBriefResponseDto(BaseModel):
    review_id: str
    content: str
    created_at: str
    answer: Optional[ReviewAnswerResponseDto]
    user_id: str
    user_nickname: str
    user_profile_image: str
    user_visit_count: int
    tags: List[str]

    @classmethod
    def from_entity(cls, entity: Tuple[Review, int]):
        review = entity[0]
        visit_count = entity[1]
        return ReviewBriefResponseDto(
            review_id=review.id,
            content=review.content,
            created_at=get_relative_time(review.created_at),
            answer=ReviewAnswerResponseDto.from_entity(review.answer) if review.answer is not None else None,
            user_id=review.user.id,
            user_nickname=review.user.nickname,
            user_profile_image=review.user.profile_img,
            user_visit_count=visit_count,
            tags=[e.word for e in review.tag]
        )


class ReviewTagDto(BaseModel):
    tag: str
    count: int


class ReviewSummaryResponseDto(BaseModel):
    center_id: str
    center_name: str
    count_total: int
    count_not_answered: int
    count_answered: int
    review_count_by_tag_list: List[ReviewTagDto]

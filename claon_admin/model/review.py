from collections import Counter
from datetime import date
from typing import List, Tuple

from pydantic import BaseModel, validator, root_validator

from claon_admin.common.util.time import get_relative_time
from claon_admin.schema.center import Review, ReviewAnswer, Center


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
        return cls(
            review_answer_id=entity.id,
            content=entity.content,
            created_at=get_relative_time(entity.created_at),
            review_id=entity.review.id
        )


class ReviewBriefResponseDto(BaseModel):
    review_id: str
    content: str
    created_at: str
    answer: ReviewAnswerResponseDto | None
    user_id: str
    user_nickname: str
    user_profile_image: str
    user_visit_count: int
    tags: List[str]

    @classmethod
    def from_entity(cls, entity: Tuple[Review, int]):
        review, visit_count = entity
        return cls(
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
    count_by_tag: List[ReviewTagDto]

    @classmethod
    def from_entity(cls, center: Center, counts: Counter, count_by_tag: List[ReviewTagDto]):
        return cls(
            center_id=center.id,
            center_name=center.name,
            count_total=counts[False] + counts[True],
            count_not_answered=counts[False],
            count_answered=counts[True],
            count_by_tag=count_by_tag
        )


class ReviewFinder(BaseModel):
    start_date: date
    end_date: date
    tag: str | None
    is_answered: bool | None

    @root_validator
    def validate_time_range(cls, values):
        if values.get('start_date') > values.get('end_date'):
            raise ValueError("시작 날짜와 종료 날짜를 확인해 주세요.")
        return values

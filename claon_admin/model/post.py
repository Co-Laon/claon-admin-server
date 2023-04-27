from typing import List

from pydantic import BaseModel


class PostBriefResponseDto(BaseModel):
    post_id: str
    content: str
    image: str
    created_at: str
    user_id: str
    user_nickname: str
    user_profile_image: str


class PostCount(BaseModel):
    unit: str
    count: int


class PostSummaryResponseDto(BaseModel):
    center_id: str
    center_name: str
    count_today: int
    count_week: int
    count_month: int
    count_total: int
    count_per_day: List[PostCount]
    count_per_week: List[PostCount]


class PostCommentResponseDto(BaseModel):
    user_id: str
    user_nickname: str
    user_profile_image: str
    created_at: str
    content: str
    child_count: int


class ClimbingHistoryDto(BaseModel):
    hold_id: str
    image: str
    count: int


class PostResponseDto(BaseModel):
    post_id: str
    content: str
    images: List[str]
    like_count: int
    climbing_history: List[ClimbingHistoryDto]
    created_at: str
    user_id: str
    user_nickname: str
    user_profile_image: str

from typing import List

from pydantic import BaseModel

from claon_admin.common.util.time import get_relative_time
from claon_admin.schema.center import Post


class PostBriefResponseDto(BaseModel):
    post_id: str
    content: str
    image: str
    created_at: str
    user_id: str
    user_nickname: str
    user_profile_image: str

    @classmethod
    def from_entity(cls, entity: Post):
        return PostBriefResponseDto(
            post_id=entity.id,
            content=entity.content,
            image=entity.img[0].url,
            created_at=get_relative_time(entity.created_at),
            user_id=entity.user.id,
            user_nickname=entity.user.nickname,
            user_profile_image=entity.user.profile_img
        )


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

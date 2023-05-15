from typing import List

from pydantic import BaseModel

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
            created_at=entity.created_at.strftime("%Y-%m-%d %H:%M:%S"),
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

    @classmethod
    def from_entity(cls, center_id: str, center_name: str, count_list: List):
        return PostSummaryResponseDto(
            center_id=center_id,
            center_name=center_name,
            count_today=count_list[0],
            count_week=count_list[1],
            count_month=count_list[2],
            count_total=count_list[3],
            count_per_day=count_list[4],
            count_per_week=count_list[5]
        )


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

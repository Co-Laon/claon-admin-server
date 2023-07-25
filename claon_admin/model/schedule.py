from datetime import datetime
from typing import List

from pydantic import BaseModel, validator
from claon_admin.schema.center import CenterSchedule


class ScheduleRequestDto(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    member_list: List[str]
    description: str | None

    @validator("title")
    def validate_title(cls, value):
        if len(value) > 20:
            raise ValueError("제목은 20자 이하로 입력해 주세요.")

    @validator("description")
    def validate_description(cls, value):
        if len(value) > 255:
            raise ValueError("설명은 255자 이하로 입력해 주세요.")


class ScheduleBriefResponseDto(BaseModel):
    schedule_id: str
    title: str
    start_time: datetime
    end_time: datetime

    @classmethod
    def from_entity(cls, entity: CenterSchedule):
        return cls(
            schedule_id=entity.id,
            title=entity.title,
            start_time=entity.start_time,
            end_time=entity.start_time
        )


class MemberDto(BaseModel):
    user_id: str
    nickname: str
    profile_image: str


class ScheduleResponseDto(BaseModel):
    schedule_id: str
    title: str
    start_time: datetime
    end_time: datetime
    member_list: List[MemberDto]
    description: str | None

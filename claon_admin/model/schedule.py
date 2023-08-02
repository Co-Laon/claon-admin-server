from datetime import datetime
from typing import List

from pydantic import BaseModel, validator, root_validator

from claon_admin.schema.center import CenterSchedule
from claon_admin.schema.user import User


class ScheduleInfoDto(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    description: str | None

    @root_validator
    def validate_time_range(cls, values):
        if values.get('start_time') > values.get('end_time'):
            raise ValueError("시작 날짜와 종료 날짜를 확인해 주세요.")
        return values

    @validator("title")
    def validate_title(cls, value):
        if len(value) > 20:
            raise ValueError("제목은 20자 이하로 입력해 주세요.")
        return value

    @validator("description")
    def validate_description(cls, value):
        if len(value) > 255:
            raise ValueError("설명은 255자 이하로 입력해 주세요.")
        return value


class ScheduleRequestDto(BaseModel):
    member_list: List[str]
    schedule_info: ScheduleInfoDto


class ScheduleBriefResponseDto(BaseModel):
    schedule_id: str
    title: str
    start_time: datetime
    end_time: datetime


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

    @classmethod
    def from_entity(cls, schedule: CenterSchedule, users: List[User]):
        return cls(
            schedule_id=schedule.id,
            title=schedule.title,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            member_list=[MemberDto(user_id=user.id,
                                   nickname=user.nickname,
                                   profile_image=user.profile_img) for user in users],
            description=schedule.description
        )

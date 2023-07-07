from typing import List

from pydantic import BaseModel, validator

from claon_admin.common.enum import MembershipStatus, CenterFeeType
from claon_admin.model.center import CenterFeeResponseDto


class CenterMemberSummaryResponseDto(BaseModel):
    count_total: int
    count_new: int
    count_leave_total: int


class CenterMemberBriefResponseDto(BaseModel):
    profile_img: str
    nickname: str
    email: str
    status: str
    extended_count: int
    registration_date: str
    memo: str | None


class MembershipDto(BaseModel):
    name: str
    fee_type: CenterFeeType
    expiration_date: str
    remaining_count: int | None
    status: MembershipStatus


class CenterMemberDetailResponseDto(BaseModel):
    profile_img: str
    nickname: str
    email: str
    memo: str | None
    histories: List[MembershipDto]


class MembershipSummaryResponseDto(BaseModel):
    count_new: int
    count_use: int
    count_expired: int


class MembershipResponseDto(BaseModel):
    membership_id: str
    member_profile_img: str
    member_nickname: str
    member_email: str
    center_fee: CenterFeeResponseDto
    start_time: str
    expire_time: str
    status: MembershipStatus


class MembershipIssueRequestDto(BaseModel):
    member_nicknames: List[str]
    center_id: str
    center_fee_id: str
    start_time: str
    expire_time: str

    @validator('member_nicknames')
    def validate_member_nicknames(cls, value):
        if len(value) > 18:
            raise ValueError('최대 18명까지 회원권을 발급할 수 있습니다.')
        return value


class MembershipIssueResponseDto(BaseModel):
    membership_ids: List[str]
    member_nicknames: List[str]
    center_fee: CenterFeeResponseDto
    start_time: str
    expire_time: str


class MembershipCountUpdateRequestDto(BaseModel):
    membership_ids = List[str]


class MembershipExpireRequestDto(BaseModel):
    membership_ids = List[str]

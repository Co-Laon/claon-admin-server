from typing import List

from pydantic import BaseModel, validator


class MemberSummaryResponseDto(BaseModel):
    count_total: int
    count_new: int
    count_leave_total: int


class MemberBriefResponseDto(BaseModel):
    profile_img: str
    nickname: str
    email: str
    status: str
    extended_count: int
    registration_date: str
    memo: str | None


class MembershipDto(BaseModel):
    name: str
    type: str
    price: int
    count: int | None
    period: int
    period_type: str


class IssuedMembershipFindDto(BaseModel):
    name: str
    type: str
    expiration_date: str
    remaining_count: int | None
    status: str


class MemberDetailResponseDto(BaseModel):
    profile_img: str
    nickname: str
    email: str
    memo: str | None
    memberships: List[IssuedMembershipFindDto]


class MembershipRequestDto(BaseModel):
    name: str
    type: str
    period: int
    period_unit: str
    count: int | None
    price: int

    @validator('name')
    def validate_name(cls, value):
        if not len(value) > 2 and len(value) < 20:
            raise ValueError('회원권 이름은 2~20자 이하로 입력해 주세요.')
        return value

    @validator('period')
    def validate_period(cls, value):
        if not isinstance(value, int):
            raise ValueError('기간은 자연수만 입력해 주세요.')
        return value

    @validator('count')
    def validate_count(cls, value):
        if value is not None and not isinstance(value, int):
            raise ValueError('횟수는 자연수만 입력해 주세요.')
        return value

    @validator('price')
    def validate_price(cls, value):
        if not isinstance(value, int):
            raise ValueError('가격은 자연수만 입력해 주세요.')
        return value


class MembershipResponseDto(BaseModel):
    id: str
    membership: MembershipDto


class IssuedMembershipSummaryResponseDto(BaseModel):
    count_new: int
    count_use: int
    count_expired: int


class IssuedMembershipBriefResponseDto(BaseModel):
    member_profile_img: str
    member_nickname: str
    member_email: str
    issued_membership: MembershipDto
    start_time: str
    expired_time: str
    status: str


class MembershipIssueRequestDto(BaseModel):
    member_nicknames: List[str]
    membership: MembershipDto
    start_time: str
    expired_time: str

    @validator('member_nicknames')
    def validate_member_nicknames(cls, value):
        if len(value) > 18:
            raise ValueError('최대 18명까지 회원권을 발급할 수 있습니다.')
        return value


class MembershipIssueResponseDto(BaseModel):
    member_ids: List[str]
    member_nicknames: List[str]
    issued_membership: MembershipDto
    start_time: str
    expired_time: str


class IssuedMembershipResponseDto(BaseModel):
    id: str
    issued_membership: MembershipDto

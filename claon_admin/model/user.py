from datetime import date
from typing import Optional, List

from pydantic import BaseModel, EmailStr, validator

from claon_admin.config.consts import KOR_BEGIN_CODE, KOR_END_CODE
from claon_admin.model.enum import SignUpRole


class SignInRequestDto(BaseModel):
    id_token: str


class IsDuplicatedNicknameResponseDto(BaseModel):
    is_duplicated: bool


class UserProfileDto(BaseModel):
    profile_image: Optional[str]
    nickname: str
    email: EmailStr
    instagram_nickname: Optional[str]
    role: Optional[SignUpRole]

    @validator('nickname')
    def validate_nickname(cls, value):
        for c in value:
            if not (('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('닉네임은 한글, 영문, 숫자로만 입력 해주세요.')
        if len(value) < 2 or len(value) > 20:
            raise ValueError('닉네임은 2자 이상 20자 이하로 입력 해주세요.')
        return value

    @validator('instagram_nickname')
    def validate_instagram_nickname(cls, value):
        for c in value:
            if not (('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('인스타그램 닉네임은 한글, 영문, 숫자로만 입력 해주세요.')
        if value is not None and (len(value) < 3 or len(value) > 30):
            raise ValueError('인스타그램 닉네임은 3자 이상 30자 이하로 입력 해주세요.')
        return value


class JwtResponseDto(BaseModel):
    access_token: str
    refresh_token: str
    is_signed_up: bool
    profile: UserProfileDto


class UserProfileResponseDto(BaseModel):
    is_proofed: bool
    profile: UserProfileDto


class LectorContestDto(BaseModel):
    year: int
    title: str
    name: str

    @validator('year')
    def validate_year(cls, value):
        if len(str(value)) != 4:
            raise ValueError('연도는 4자리로 입력 해주세요.')
        if value < 1976:
            raise ValueError('연도는 1976년 이후로 입력 해주세요.')
        return value

    @validator('title')
    def validate_title(cls, value):
        for c in value:
            if not (('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('수상명은 한글, 영문, 숫자로만 입력 해주세요.')
        if len(value) < 1 or len(value) > 50:
            raise ValueError('수상명은 50자 이하로 입력 해주세요.')
        return value

    @validator('name')
    def validate_name(cls, value):
        for c in value:
            if not (('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('대회명은 한글, 영문, 숫자로만 입력 해주세요.')
        if len(value) < 1 or len(value) > 50:
            raise ValueError('대회명은 50자 이하로 입력 해주세요.')
        return value


class LectorCertificateDto(BaseModel):
    acquisition_date: date
    rate: int
    name: str

    @validator('rate')
    def validate_rate(cls, value):
        if value < 1 or value > 99:
            raise ValueError('급수는 1 이상 100미만 으로 입력 해주세요.')
        return value

    @validator('name')
    def validate_name(cls, value):
        for c in value:
            if not (('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('자격증명은 한글, 영문, 숫자로만 입력 해주세요.')
        if len(value) < 1 or len(value) > 50:
            raise ValueError('자격증명은 50자 이하로 입력 해주세요.')
        return value


class LectorCareerDto(BaseModel):
    start_date: date
    end_date: date
    name: str

    @validator('name')
    def validate_name(cls, value):
        for c in value:
            if not (('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('경력명은 한글, 영문, 숫자로만 입력 해주세요.')
        if len(value) < 1 or len(value) > 50:
            raise ValueError('경력명은 50자 이하로 입력 해주세요.')
        return value


class LectorRequestDto(BaseModel):
    profile: UserProfileDto
    is_setter: bool
    contest_list: List[LectorContestDto]
    certificate_list: List[LectorCertificateDto]
    career_list: List[LectorCareerDto]
    proof_list: List[str]

    @validator('proof_list')
    def validate_proof_list(cls, value):
        if len(value) > 5:
            raise ValueError('증빙자료는 5개 이하로 입력 해주세요.')
        return value\

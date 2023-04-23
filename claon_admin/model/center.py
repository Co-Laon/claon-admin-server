import re
from typing import List, Optional

from pydantic import BaseModel, validator

from claon_admin.config.consts import KOR_BEGIN_CODE, KOR_END_CODE
from claon_admin.common.enum import WallType
from claon_admin.model.user import UserProfileDto
from claon_admin.schema.center import Center


class CenterOperatingTimeDto(BaseModel):
    day_of_week: str
    start_time: str
    end_time: str

    @validator('day_of_week')
    def validate_day_of_week(cls, value):
        if value not in ['월', '화', '수', '목', '금', '토', '일', '공휴일']:
            raise ValueError('요일은 월, 화, 수, 목, 금, 토, 일 중 하나로 입력해 주세요.')
        return value

    @validator('start_time')
    def validate_start_time(cls, value):
        if not re.match(r'^(0\d|1\d|2[0-3]):(0[1-9]|[0-5]\d)$', value):
            raise ValueError('올바른 시간 형식으로 입력해 주세요.')
        return value

    @validator('end_time')
    def validate_end_time(cls, value):
        if not re.match(r'^(0\d|1\d|2[0-3]):(0[1-9]|[0-5]\d)$', value):
            raise ValueError('올바른 시간 형식으로 입력해 주세요.')
        return value


class CenterFeeDto(BaseModel):
    name: str
    price: int
    count: int

    @validator('name')
    def validate_name(cls, value):
        if len(value) < 2 or len(value) > 50:
            raise ValueError('이름은 2자 이상 50자 이하로 입력해 주세요.')
        return value

    @validator('price')
    def validate_price(cls, value):
        if value < 0:
            raise ValueError('가격은 0원 이상으로 입력해 주세요.')
        return value

    @validator('count')
    def validate_count(cls, value):
        if value < 0:
            raise ValueError('횟수는 0회 이상으로 입력해 주세요.')
        return value


class CenterHoldDto(BaseModel):
    difficulty: str
    name: str
    is_color: bool

    @validator('difficulty')
    def validate_difficulty(cls, value):
        if len(value) < 2 or len(value) > 10:
            raise ValueError('홀드 난이도는 1자 이상 10자 이하로 입력해 주세요.')
        return value

    @validator('name')
    def validate_name(cls, value):
        if len(value) < 2 or len(value) > 10:
            raise ValueError('홀드 이름은 1자 이상 10자 이하로 입력해 주세요.')
        return value


class CenterWallDto(BaseModel):
    wall_type: WallType
    name: str

    @validator('name')
    def validate_name(cls, value):
        if len(value) < 2 or len(value) > 20:
            raise ValueError('벽 이름은 2자 이상 20자 이하로 입력해 주세요.')
        return value


class CenterNameResponseDto(BaseModel):
    center_id: str
    name: str
    address: str


class CenterRequestDto(BaseModel):
    profile_image: str
    name: str
    address: str
    detail_address: Optional[str]
    tel: str
    web_url: Optional[str]
    instagram_name: Optional[str]
    youtube_code: Optional[str]
    image_list: List[str]
    utility_list: List[str]
    fee_image_list: List[str]
    operating_time_list: List[CenterOperatingTimeDto]
    fee_list: List[CenterFeeDto]
    hold_list: List[CenterHoldDto]
    wall_list: List[CenterWallDto]
    proof_list: List[str]

    @validator('name')
    def validate_name(cls, value):
        for c in value:
            if not ((c == ' ') or ('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('암장명은 한글, 영문, 숫자로만 입력해 주세요.')
        if len(value) < 2 or len(value) > 50:
            raise ValueError('암장명은 2자 이상 50자 이하로 입력해 주세요.')
        return value

    @validator('tel', pre=True, always=True)
    def validate_tel(cls, value):
        if not re.match(r'^(0)\d{1,2}-\d{3,4}-\d{4}$', value):
            raise ValueError('전화번호를 올바른 형식으로 다시 입력해주세요.')
        return value

    @validator('instagram_name')
    def validate_instagram_name(cls, value):
        if value is None:
            return value

        for c in value:
            if not ((c == '_') or (c == '.') or ('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('인스타그램 닉네임은 한글, 영문, 숫자로만 입력해 주세요.')
        if len(value) < 3 or len(value) > 30:
            raise ValueError('인스타그램 닉네임은 3자 이상 30자 이하로 입력해 주세요.')
        return value

    @validator('youtube_code')
    def validate_youtube_code(cls, value):
        if value is None:
            return value

        if value[0] != "@":
            raise ValueError('유튜브 채널 코드는 @로 시작해 주세요.')
        return value

    @validator('image_list')
    def validate_image_list(cls, value):
        if len(value) > 10:
            raise ValueError('이미지는 최대 10장까지 등록 가능해요.')
        return value

    @validator('fee_image_list')
    def validate_fee_image_list(cls, value):
        if len(value) > 5:
            raise ValueError('이용요금 이미지는 최대 10장까지 등록 가능해요.')
        return value

    @validator('operating_time_list')
    def validate_operating_time_list(cls, value):
        if len(value) > 8:
            raise ValueError('운영시간은 최대 8개까지 등록 가능해요.')
        return value

    @validator('proof_list')
    def validate_proof_list(cls, value):
        if len(value) > 5:
            raise ValueError('증빙자료는 5개 이하로 입력해 주세요.')
        return value


class CenterUpdateRequestDto(BaseModel):
    profile_image: str
    tel: str
    web_url: Optional[str]
    instagram_name: Optional[str]
    youtube_code: Optional[str]
    image_list: List[str]
    utility_list: List[str]
    fee_image_list: List[str]
    operating_time_list: List[CenterOperatingTimeDto]
    fee_list: List[CenterFeeDto]
    hold_list: List[CenterHoldDto]
    wall_list: List[CenterWallDto]

    @validator('tel', pre=True, always=True)
    def validate_tel(cls, value):
        if not re.match(r'^(0)\d{1,2}-\d{3,4}-\d{4}$', value):
            raise ValueError('전화번호를 올바른 형식으로 다시 입력해 주세요.')
        return value

    @validator('instagram_name')
    def validate_instagram_name(cls, value):
        if value is None:
            return value

        for c in value:
            if not ((c == '_') or (c == '.') or ('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('인스타그램 닉네임은 한글, 영문, 숫자로만 입력해 주세요.')
        if len(value) < 3 or len(value) > 30:
            raise ValueError('인스타그램 닉네임은 3자 이상 30자 이하로 입력해 주세요.')
        return value

    @validator('youtube_code')
    def validate_youtube_code(cls, value):
        if value is None:
            return value

        if value[0] != "@":
            raise ValueError('유튜브 채널 코드는 @로 시작해 주세요.')
        return value

    @validator('image_list')
    def validate_image_list(cls, value):
        if len(value) > 10:
            raise ValueError('이미지는 최대 10장까지 등록 가능해요.')
        return value

    @validator('fee_image_list')
    def validate_fee_image_list(cls, value):
        if len(value) > 5:
            raise ValueError('이용요금 이미지는 최대 10장까지 등록 가능해요.')
        return value

    @validator('operating_time_list')
    def validate_operating_time_list(cls, value):
        if len(value) > 8:
            raise ValueError('운영시간은 최대 8개까지 등록 가능해요.')
        return value


class CenterResponseDto(BaseModel):
    center_id: str
    profile_image: str
    name: str
    address: str
    detail_address: Optional[str]
    tel: str
    web_url: Optional[str]
    instagram_name: Optional[str]
    youtube_code: Optional[str]
    image_list: List[str]
    utility_list: List[str]
    fee_image_list: List[str]
    operating_time_list: List[CenterOperatingTimeDto]
    fee_list: List[CenterFeeDto]
    hold_list: List[CenterHoldDto]
    wall_list: List[CenterWallDto]
    approved: bool

    @classmethod
    def from_entity(cls, entity: Center):
        return CenterResponseDto(
            center_id=entity.id,
            profile_image=entity.profile_img,
            name=entity.name,
            address=entity.address,
            detail_address=entity.detail_address if entity.detail_address is not None else None,
            tel=entity.tel,
            web_url=entity.web_url if entity.web_url is not None else None,
            instagram_name=entity.instagram_name if entity.instagram_name is not None else None,
            youtube_code=str(entity.youtube_url).split("/")[-1] if entity.youtube_url is not None else None,
            image_list=[e.url for e in entity.center_img],
            utility_list=[e.name for e in entity.utility],
            fee_image_list=[e.url for e in entity.fee_img],
            operating_time_list=[
                CenterOperatingTimeDto(day_of_week=e.day_of_week, start_time=e.start_time, end_time=e.end_time)
                for e in entity.operating_time
            ],
            fee_list=[
                CenterFeeDto(name=e.name, price=e.price, count=e.count)
                for e in entity.fees
            ],
            hold_list=[
                CenterHoldDto(difficulty=e.difficulty, name=e.name, is_color=e.is_color)
                for e in entity.holds
            ],
            wall_list=[
                CenterWallDto(
                    wall_type=WallType.BOULDERING if e.type == "bouldering" else WallType.ENDURANCE,
                    name=e.name
                ) for e in entity.walls
            ],
            approved=entity.approved
        )


class CenterBriefResponseDto(BaseModel):
    center_id: str
    profile_image: str
    name: str
    address: str
    detail_address: Optional[str]
    image_list: List[str]
    lector_count: Optional[int]
    member_count: Optional[int]
    matching_request_count: Optional[int]
    is_approved: bool


class CenterAuthRequestDto(BaseModel):
    profile: UserProfileDto
    profile_image: str
    name: str
    address: str
    detail_address: Optional[str]
    tel: str
    web_url: Optional[str]
    instagram_name: Optional[str]
    youtube_code: Optional[str]
    image_list: List[str]
    utility_list: List[str]
    fee_image_list: List[str]
    operating_time_list: List[CenterOperatingTimeDto]
    fee_list: List[CenterFeeDto]
    hold_list: List[CenterHoldDto]
    wall_list: List[CenterWallDto]
    proof_list: List[str]

    @validator('name')
    def validate_name(cls, value):
        for c in value:
            if not ((c == ' ') or ('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('암장명은 한글, 영문, 숫자로만 입력해 주세요.')
        if len(value) < 2 or len(value) > 50:
            raise ValueError('암장명은 2자 이상 50자 이하로 입력해 주세요.')
        return value

    @validator('tel', pre=True, always=True)
    def validate_tel(cls, value):
        if not re.match(r'^(0)\d{1,2}-\d{3,4}-\d{4}$', value):
            raise ValueError('전화번호를 올바른 형식으로 다시 입력해 주세요.')
        return value

    @validator('instagram_name')
    def validate_instagram_name(cls, value):
        if value is None:
            return value

        for c in value:
            if not ((c == '_') or (c == '.') or ('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('인스타그램 닉네임은 한글, 영문, 숫자로만 입력해 주세요.')
        if len(value) < 3 or len(value) > 30:
            raise ValueError('인스타그램 닉네임은 3자 이상 30자 이하로 입력해 주세요.')
        return value

    @validator('youtube_code')
    def validate_youtube_code(cls, value):
        if value is None:
            return value

        if value[0] != "@":
            raise ValueError('유튜브 채널 코드는 @로 시작해 주세요.')
        return value

    @validator('image_list')
    def validate_image_list(cls, value):
        if len(value) > 10:
            raise ValueError('이미지는 최대 10장까지 등록 가능해요.')
        return value

    @validator('fee_image_list')
    def validate_fee_image_list(cls, value):
        if len(value) > 5:
            raise ValueError('이용요금 이미지는 최대 10장까지 등록 가능해요.')
        return value

    @validator('operating_time_list')
    def validate_operating_time_list(cls, value):
        if len(value) > 8:
            raise ValueError('운영시간은 최대 8개까지 등록 가능해요.')
        return value

    @validator('proof_list')
    def validate_proof_list(cls, value):
        if len(value) > 5:
            raise ValueError('증빙자료는 5개 이하로 입력해 주세요.')
        return value


class UploadFileResponseDto(BaseModel):
    file_url: str

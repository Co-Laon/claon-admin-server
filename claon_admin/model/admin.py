from datetime import date
from typing import Optional, List

from pydantic import BaseModel

from claon_admin.model.enum import WallType


class CenterOperatingTimeDto(BaseModel):
    day_of_week: str
    start_time: str
    end_time: str


class CenterFeeDto(BaseModel):
    name: str
    price: int
    count: int


class CenterHoldDto(BaseModel):
    difficulty: str
    name: str


class CenterWallDto(BaseModel):
    wall_type: WallType
    name: str


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
    proof_list: List[str]


class LectorContestDto(BaseModel):
    year: int
    title: str
    name: str


class LectorCertificateDto(BaseModel):
    acquisition_date: date
    rate: int
    name: str


class LectorCareerDto(BaseModel):
    start_date: date
    end_date: date
    name: str


class LectorResponseDto(BaseModel):
    is_setter: bool
    contest_list: List[LectorContestDto]
    certificate_list: List[LectorCertificateDto]
    career_list: List[LectorCareerDto]
    proof_list: List[str]

from datetime import date
from typing import List

from pydantic import BaseModel

from claon_admin.common.enum import WallType, CenterFeeType, PeriodType
from claon_admin.model.user import UserProfileResponseDto
from claon_admin.schema.center import Center, CenterApprovedFile
from claon_admin.schema.user import Lector, LectorApprovedFile


class CenterOperatingTimeDto(BaseModel):
    day_of_week: str
    start_time: str
    end_time: str


class CenterFeeDto(BaseModel):
    center_fee_id: str
    name: str
    fee_type: CenterFeeType
    price: int
    count: int | None
    period: int
    period_type: PeriodType


class CenterHoldDto(BaseModel):
    difficulty: str
    name: str


class CenterHoldInfoDto(BaseModel):
    is_color: bool
    hold_list: List[CenterHoldDto]


class CenterWallDto(BaseModel):
    wall_type: WallType
    name: str


class CenterResponseDto(BaseModel):
    user_profile: UserProfileResponseDto
    center_id: str
    profile_image: str
    name: str
    address: str
    detail_address: str | None
    tel: str
    web_url: str | None
    instagram_name: str | None
    youtube_code: str | None
    approved: bool
    image_list: List[str]
    utility_list: List[str]
    fee_image_list: List[str]
    operating_time_list: List[CenterOperatingTimeDto]
    fee_list: List[CenterFeeDto]
    hold_list: CenterHoldInfoDto | None
    wall_list: List[CenterWallDto]
    proof_list: List[str]

    @classmethod
    def from_entity(cls, center: Center, approved_files: List[CenterApprovedFile]):
        return CenterResponseDto(
            user_profile=UserProfileResponseDto.from_entity(center.user),
            center_id=center.id,
            profile_image=center.profile_img,
            name=center.name,
            address=center.address,
            detail_address=center.detail_address if center.detail_address is not None else None,
            tel=center.tel,
            web_url=center.web_url if center.web_url is not None else None,
            instagram_name=center.instagram_name if center.instagram_name is not None else None,
            youtube_code=center.youtube_url.rsplit("/", maxsplit=1)[-1] if center.youtube_url is not None else None,
            approved=center.approved,
            image_list=[e.url for e in center.center_img],
            utility_list=[e.name for e in center.utility],
            fee_image_list=[],
            operating_time_list=[
                CenterOperatingTimeDto(day_of_week=e.day_of_week, start_time=e.start_time, end_time=e.end_time)
                for e in center.operating_time
            ],
            fee_list=[],
            hold_info=CenterHoldInfoDto(
                is_color=center.holds[0].is_color,
                hold_list=[CenterHoldInfoDto(difficulty=e.difficulty, name=e.name)
                           for e in center.holds or []]
            ) if center.holds else None,
            wall_list=[CenterWallDto(
                wall_type=WallType.BOULDERING if e.type == "bouldering" else WallType.ENDURANCE,
                name=e.name
            ) for e in center.walls or []],
            proof_list=[e.url for e in approved_files]
        )


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
    lector_id: str
    user_profile: UserProfileResponseDto
    is_setter: bool
    approved: bool
    contest_list: List[LectorContestDto]
    certificate_list: List[LectorCertificateDto]
    career_list: List[LectorCareerDto]
    proof_list: List[str]

    @classmethod
    def from_entity(cls, lector: Lector, approved_files: List[LectorApprovedFile]):
        return LectorResponseDto(
            lector_id=lector.id,
            user_profile=UserProfileResponseDto.from_entity(lector.user),
            is_setter=lector.is_setter,
            approved=lector.approved,
            contest_list=[LectorContestDto(year=e.year, title=e.title, name=e.name) for e in lector.contest],
            certificate_list=[LectorCertificateDto(
                acquisition_date=e.acquisition_date,
                rate=e.rate,
                name=e.name
            ) for e in lector.certificate],
            career_list=[LectorCareerDto(
                start_date=e.start_date,
                end_date=e.end_date,
                name=e.name
            ) for e in lector.career],
            proof_list=[e.url for e in approved_files]
        )

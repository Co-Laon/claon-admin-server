from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import BadRequestException, ErrorCode
from claon_admin.model.center import CenterRequestDto, CenterResponseDto
from claon_admin.model.enum import Role
from claon_admin.model.user import IsDuplicatedNicknameResponseDto, LectorRequestDto, LectorResponseDto
from claon_admin.schema.center import CenterRepository, Center, CenterImage, OperatingTime, Utility, CenterFee, \
    CenterFeeImage, CenterHold, CenterWall, CenterApprovedFile
from claon_admin.schema.user import UserRepository, LectorRepository, Lector, Contest, Certificate, Career, \
    LectorApprovedFile, LectorApprovedFileRepository


class UserService:
    def __init__(self,
                 user_repository: UserRepository,
                 lector_repository: LectorRepository,
                 center_repository: CenterRepository,
                 lector_approved_file_repository: LectorApprovedFileRepository):
        self.user_repository = user_repository
        self.lector_repository = lector_repository
        self.center_repository = center_repository
        self.lector_approved_file_repository = lector_approved_file_repository

    async def sign_up_center(self, session: AsyncSession, dto: CenterRequestDto):
        if dto.profile.role != Role.PENDING:
            raise BadRequestException(
                ErrorCode.USER_ALREADY_SIGNED_UP,
                "Current user is already signed up."
            )

        user = await self.user_repository.find_by_nickname(session, dto.profile.nickname)
        center = await self.center_repository.save(session, Center(
            user_id=user.id,
            user=user,
            name=dto.name,
            profile_img=dto.profile_image,
            address=dto.address,
            detail_address=dto.detail_address,
            tel=dto.tel,
            web_url=dto.web_url,
            instagram_name=dto.instagram_name,
            youtube_url="https://www.youtube.com/%s" % str(dto.youtube_code),
            center_img=[CenterImage(url=e) for e in dto.image_list],
            operating_time=[
                OperatingTime(day_of_week=e.day_of_week, start_time=e.start_time, end_time=e.end_time)
                for e in dto.operating_time_list
            ],
            utility=[Utility(name=e) for e in dto.utility_list],
            fee=[CenterFee(name=e.name, price=e.price, count=e.count) for e in dto.fee_list],
            fee_img=[CenterFeeImage(url=e) for e in dto.fee_image_list],
            holds=[
                CenterHold(name=e.name, difficulty=e.difficulty, is_color=e.is_color)
                for e in dto.hold_list
            ],
            walls=[CenterWall(name=e.name, type=e.wall_type.value) for e in dto.wall_list],
            approved=False
        ))

        return CenterResponseDto.from_entity(center)

    async def sign_up_lector(self, session: AsyncSession, dto: LectorRequestDto):
        if dto.profile.role != Role.PENDING:
            raise BadRequestException(
                ErrorCode.USER_ALREADY_SIGNED_UP,
                "Current user is already signed up."
            )

        total_experience = 0
        for career in dto.career_list:
            total_experience += (career.end_date - career.start_date).total_seconds()
        user = await self.user_repository.find_by_nickname(session, dto.profile.nickname)

        lector = await self.lector_repository.save(session, Lector(
            user_id=user.id,
            user=user,
            is_setter=dto.is_setter,
            total_experience=total_experience // (365 * 24 * 60 * 60),
            contest=[Contest(year=e.year, title=e.title, name=e.name) for e in dto.contest_list],
            certificate=[
                Certificate(acquisition_date=e.acquisition_date, rate=e.rate, name=e.name)
                for e in dto.certificate_list
            ],
            career=[
                Career(start_date=e.start_date, end_date=e.end_date, name=e.name)
                for e in dto.career_list
            ],
            approved=False
        ))

        [await self.lector_approved_file_repository.save(session, LectorApprovedFile(lector=lector, url=e))
         for e in dto.proof_list]

        return LectorResponseDto.from_entity(lector)

    async def check_nickname_duplication(self, session: AsyncSession, nickname: str):
        if await self.user_repository.exist_by_nickname(session, nickname):
            return IsDuplicatedNicknameResponseDto(is_duplicated=True)
        return IsDuplicatedNicknameResponseDto(is_duplicated=False)

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import BadRequestException, ErrorCode
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterRequestDto, CenterResponseDto
from claon_admin.model.user import IsDuplicatedNicknameResponseDto, LectorRequestDto, LectorResponseDto, UserProfileResponseDto
from claon_admin.schema.center import CenterRepository, Center, CenterImage, OperatingTime, Utility, CenterFee, \
    CenterFeeImage, CenterHold, CenterWall, CenterApprovedFile, CenterHoldRepository, CenterWallRepository, \
    CenterApprovedFileRepository
from claon_admin.schema.user import UserRepository, LectorRepository, Lector, Contest, Certificate, Career, \
    LectorApprovedFile, LectorApprovedFileRepository, User
from claon_admin.common.util.jwt import create_access_token, create_refresh_token
from claon_admin.infra.provider import OAuthUserInfoProviderSupplier, UserInfoProvider
from claon_admin.model.auth import OAuthUserInfoDto
from claon_admin.model.enum import OAuthProvider, Role
from claon_admin.model.user import SignInRequestDto, JwtResponseDto


class UserService:
    def __init__(self,
                 user_repository: UserRepository,
                 lector_repository: LectorRepository,
                 lector_approved_file_repository: LectorApprovedFileRepository,
                 center_repository: CenterRepository,
                 center_approved_file_repository: CenterApprovedFileRepository,
                 center_hold_repository: CenterHoldRepository,
                 center_wall_repository: CenterWallRepository,
                 oauth_user_info_provider_supplier: OAuthUserInfoProviderSupplier):
        self.user_repository = user_repository
        self.lector_repository = lector_repository
        self.lector_approved_file_repository = lector_approved_file_repository
        self.center_repository = center_repository
        self.center_approved_file_repository = center_approved_file_repository
        self.center_hold_repository = center_hold_repository
        self.center_wall_repository = center_wall_repository
        self.supplier = oauth_user_info_provider_supplier

    async def check_nickname_duplication(self, session: AsyncSession, nickname: str):
        is_duplicated = await self.user_repository.exist_by_nickname(session, nickname)
        return IsDuplicatedNicknameResponseDto(is_duplicated=is_duplicated)

    async def sign_up_center(self, session: AsyncSession, subject: RequestUser, dto: CenterRequestDto):
        if subject.role != Role.PENDING:
            raise BadRequestException(
                ErrorCode.USER_ALREADY_SIGNED_UP,
                "이미 회원가입이 완료된 계정입니다."
            )

        if await self.user_repository.exist_by_nickname(session, dto.profile.nickname):
            raise BadRequestException(
                ErrorCode.DUPLICATED_NICKNAME,
                "이미 존재하는 닉네임입니다."
            )

        center = await self.center_repository.save(session, Center(
            user_id=subject.id,
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
            approved=False
        ))

        holds = await self.center_hold_repository.save_all(
            session,
            [CenterHold(center=center, name=e.name, difficulty=e.difficulty, is_color=e.is_color)
             for e in dto.hold_list]
        )

        walls = await self.center_wall_repository.save_all(
            session,
            [CenterWall(center=center, name=e.name, type=e.wall_type.value)
             for e in dto.wall_list]
        )

        await self.center_approved_file_repository.save_all(
            session,
            [CenterApprovedFile(user_id=subject.id, center=center, url=e)
             for e in dto.proof_list]
        )

        return CenterResponseDto.from_entity(center, holds, walls)

    async def sign_up_lector(self, session: AsyncSession, subject: RequestUser, dto: LectorRequestDto):
        if subject.role != Role.PENDING:
            raise BadRequestException(
                ErrorCode.USER_ALREADY_SIGNED_UP,
                "이미 회원가입이 완료된 계정입니다."
            )

        if await self.user_repository.exist_by_nickname(session, dto.profile.nickname):
            raise BadRequestException(
                ErrorCode.DUPLICATED_NICKNAME,
                "이미 존재하는 닉네임입니다."
            )

        lector = await self.lector_repository.save(session, Lector(
            user_id=subject.id,
            is_setter=dto.is_setter,
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

        await self.lector_approved_file_repository.save_all(
            session,
            [LectorApprovedFile(lector=lector, url=e)
             for e in dto.proof_list]
        )

        return LectorResponseDto.from_entity(lector)

    async def sign_in(self,
                      session: AsyncSession,
                      provider: OAuthProvider,
                      dto: SignInRequestDto):
        provider: UserInfoProvider = await self.supplier.get_provider(provider=provider)
        oauth_dto: OAuthUserInfoDto = await provider.get_user_info(token=dto.id_token)

        user = await self.user_repository.find_by_oauth_id_and_sns(session, oauth_dto.oauth_id, oauth_dto.sns_email)

        is_signed_up = True
        if user is None:
            is_signed_up = False
            user = User(
                oauth_id=oauth_dto.oauth_id,
                nickname=str(uuid.uuid4()),
                sns=oauth_dto.sns_email,
                role=Role.PENDING
            )
            await self.user_repository.save(session, user)

        return JwtResponseDto(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
            is_signed_up=is_signed_up,
            profile=UserProfileResponseDto(
                profile_image=user.profile_img,
                nickname=user.nickname,
                email=user.email,
                insstagram_nickname=user.instagram_name,
                role=user.role
            )
        )

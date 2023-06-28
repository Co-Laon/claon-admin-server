import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import BadRequestException, ErrorCode
from claon_admin.common.util.jwt import create_access_token, create_refresh_token
from claon_admin.common.util.transaction import transactional
from claon_admin.service.oauth import OAuthUserInfoProviderSupplier, UserInfoProvider
from claon_admin.common.util.s3 import upload_file
from claon_admin.model.auth import OAuthUserInfoDto
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterAuthRequestDto, CenterResponseDto
from claon_admin.common.enum import OAuthProvider, Role, LectorUploadPurpose, UserUploadPurpose
from claon_admin.model.file import UploadFileResponseDto
from claon_admin.model.user import IsDuplicatedNicknameResponseDto, LectorRequestDto, LectorResponseDto, \
    UserProfileResponseDto, JwtReissueDto
from claon_admin.model.user import SignInRequestDto, JwtResponseDto
from claon_admin.schema.center import CenterRepository, Center, CenterImage, OperatingTime, Utility, CenterHold, \
    CenterWall, CenterApprovedFile, CenterHoldRepository, CenterWallRepository, CenterApprovedFileRepository, \
    CenterFeeRepository
from claon_admin.schema.user import UserRepository, LectorRepository, Lector, Contest, Certificate, Career, \
    LectorApprovedFile, LectorApprovedFileRepository, User


class UserService:
    def __init__(self,
                 user_repository: UserRepository,
                 lector_repository: LectorRepository,
                 lector_approved_file_repository: LectorApprovedFileRepository,
                 center_repository: CenterRepository,
                 center_approved_file_repository: CenterApprovedFileRepository,
                 center_fee_repository: CenterFeeRepository,
                 center_hold_repository: CenterHoldRepository,
                 center_wall_repository: CenterWallRepository,
                 oauth_user_info_provider_supplier: OAuthUserInfoProviderSupplier):
        self.user_repository = user_repository
        self.lector_repository = lector_repository
        self.lector_approved_file_repository = lector_approved_file_repository
        self.center_repository = center_repository
        self.center_approved_file_repository = center_approved_file_repository
        self.center_fee_repository = center_fee_repository
        self.center_hold_repository = center_hold_repository
        self.center_wall_repository = center_wall_repository
        self.supplier = oauth_user_info_provider_supplier

    @transactional(read_only=True)
    async def check_nickname_duplication(self, session: AsyncSession, nickname: str):
        is_duplicated = await self.user_repository.exist_by_nickname(session, nickname)
        return IsDuplicatedNicknameResponseDto(is_duplicated=is_duplicated)

    @transactional()
    async def sign_up_center(self, session: AsyncSession, subject: RequestUser, dto: CenterAuthRequestDto):
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
            youtube_url=f"https://www.youtube.com/{str(dto.youtube_code)}",
            center_img=[CenterImage(url=e) for e in dto.image_list],
            operating_time=[
                OperatingTime(day_of_week=e.day_of_week, start_time=e.start_time, end_time=e.end_time)
                for e in dto.operating_time_list
            ],
            utility=[Utility(name=e) for e in dto.utility_list],
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

        user = await self.user_repository.find_by_id(session, subject.id)
        await self.user_repository.update_role(session, user, Role.NOT_APPROVED)
        return CenterResponseDto.from_entity(center, holds, walls)

    @transactional()
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

        user = await self.user_repository.find_by_id(session, subject.id)
        await self.user_repository.update_role(session, user, Role.NOT_APPROVED)
        return LectorResponseDto.from_entity(lector)

    @transactional()
    async def sign_in(self,
                      session: AsyncSession,
                      provider: OAuthProvider,
                      dto: SignInRequestDto):
        provider: UserInfoProvider = await self.supplier.get_provider(provider=provider)
        oauth_dto: OAuthUserInfoDto = await provider.get_user_info(token=dto.id_token)

        user = await self.user_repository.find_by_oauth_id_and_sns(session, oauth_dto.oauth_id, oauth_dto.sns_email)
        if user is None:
            user = await self.user_repository.save(session, User(
                oauth_id=oauth_dto.oauth_id,
                nickname=str(uuid.uuid4()),
                sns=oauth_dto.sns_email,
                profile_img="",
                role=Role.PENDING
            ))

        return JwtResponseDto(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
            is_signed_up=user.is_signed_up(),
            profile=UserProfileResponseDto.from_entity(user)
        )

    async def reissue_token(self, subject: RequestUser):
        return JwtReissueDto(access_token=create_access_token(subject.id))

    async def upload_profile(self, file: UploadFile):
        purpose = UserUploadPurpose.PROFILE
        if file.filename.split('.')[-1] not in UserUploadPurpose.get_extensions(purpose.value):
            raise BadRequestException(
                ErrorCode.INVALID_FORMAT,
                "지원하지 않는 포맷입니다."
            )

        url = await upload_file(file=file, domain="user", purpose=purpose.value)
        return UploadFileResponseDto(file_url=url)

    async def upload_file(self, purpose: LectorUploadPurpose, file: UploadFile):
        if file.filename.split('.')[-1] not in LectorUploadPurpose.get_extensions(purpose.value):
            raise BadRequestException(
                ErrorCode.INVALID_FORMAT,
                "지원하지 않는 포맷입니다."
            )

        url = await upload_file(file=file, domain="lector", purpose=purpose.value)
        return UploadFileResponseDto(file_url=url)

    # TODO: Need to be removed later
    @transactional()
    async def test_sign_in(self, session: AsyncSession, dto: SignInRequestDto):
        user = await self.user_repository.find_by_oauth_id(session, dto.id_token)

        is_signed_up = True
        if user is None:
            is_signed_up = False
            user = User(
                oauth_id=dto.id_token,
                nickname=str(uuid.uuid4()),
                sns=dto.id_token + "@gmail.com",
                email=dto.id_token + "@gmail.com",
                profile_img="",
                role=Role.PENDING
            )
            await self.user_repository.save(session, user)

        return JwtResponseDto(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
            is_signed_up=is_signed_up,
            profile=UserProfileResponseDto.from_entity(user)
        )

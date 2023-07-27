from fastapi import UploadFile
from fastapi_pagination import Params
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import CenterUploadPurpose
from claon_admin.common.error.exception import BadRequestException, ErrorCode, UnauthorizedException, NotFoundException
from claon_admin.common.util.pagination import paginate
from claon_admin.common.util.s3 import upload_file
from claon_admin.common.util.transaction import transactional
from claon_admin.model.auth import RequestUser
from claon_admin.model.file import UploadFileResponseDto
from claon_admin.model.center import CenterNameResponseDto, CenterBriefResponseDto, CenterResponseDto, \
    CenterCreateRequestDto, CenterUpdateRequestDto, CenterFeeDetailResponseDto, CenterFeeDetailRequestDto
from claon_admin.schema.center import CenterRepository, CenterHoldRepository, CenterWallRepository, \
    CenterFeeRepository, CenterHold, CenterWall, CenterFee, CenterApprovedFileRepository, Center, CenterApprovedFile, \
    CenterScheduleRepository
from claon_admin.model.schedule import ScheduleBriefResponseDto

class CenterService:
    def __init__(self,
                 center_repository: CenterRepository,
                 center_hold_repository: CenterHoldRepository,
                 center_wall_repository: CenterWallRepository,
                 center_fee_repository: CenterFeeRepository,
                 center_approved_file_repository: CenterApprovedFileRepository,
                 center_schedule_repository: CenterScheduleRepository):
        self.center_repository = center_repository
        self.center_hold_repository = center_hold_repository
        self.center_wall_repository = center_wall_repository
        self.center_fee_repository = center_fee_repository
        self.center_approved_file_repository = center_approved_file_repository
        self.center_schedule_repository = center_schedule_repository

    @transactional()
    async def create(self,
                     session: AsyncSession,
                     subject: RequestUser,
                     dto: CenterCreateRequestDto):
        center = await self.center_repository.save(session, Center.of(subject.id, **dto.center.dict()))

        holds = []
        if dto.hold_info is not None:
            hold_is_color = dto.hold_info.is_color
            holds = await self.center_hold_repository.save_all(
                session,
                [CenterHold(center=center, name=e.name, difficulty=e.difficulty, is_color=hold_is_color)
                 for e in dto.hold_info.hold_list]
            )
        walls = await self.center_wall_repository.save_all(
            session,
            [CenterWall(center=center, name=e.name, type=e.wall_type.value)
             for e in dto.wall_list]
        )

        await self.center_approved_file_repository.save_all(
            session,
            [CenterApprovedFile(user_id=subject.id, center_id=center.id, url=url) for url in dto.proof_list]
        )

        return CenterResponseDto.from_entity(entity=center, holds=holds, walls=walls)

    async def upload_file(self, purpose: CenterUploadPurpose, file: UploadFile):
        if not purpose.is_valid_extension(file.filename.split('.')[-1]):
            raise BadRequestException(
                ErrorCode.INVALID_FORMAT,
                "지원하지 않는 포맷입니다."
            )

        url = await upload_file(file=file, domain="center", purpose=purpose.value)
        return UploadFileResponseDto(file_url=url)

    @transactional(read_only=True)
    async def find_centers_by_name(self,
                                   session: AsyncSession,
                                   name: str):
        centers = await self.center_repository.find_by_name(session, name)
        return [CenterNameResponseDto.from_entity(center) for center in centers]

    @transactional(read_only=True)
    async def find_centers(self,
                           session: AsyncSession,
                           params: Params,
                           subject: RequestUser):
        pages = await self.center_repository.find_details_by_user_id(session, subject.id, params)

        if not pages.items:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "등록된 암장이 존재하지 않습니다."
            )

        return await paginate(CenterBriefResponseDto, pages)

    @transactional(read_only=True)
    async def find_by_id(self,
                         session: AsyncSession,
                         subject: RequestUser,
                         center_id: str):
        center = await self.center_repository.find_by_id_with_details(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if not center.is_owner(subject.id):
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        return CenterResponseDto.from_entity(center, center.holds, center.walls, center.fees)

    @transactional()
    async def delete(self,
                     session: AsyncSession,
                     subject: RequestUser,
                     center_id: str):
        center = await self.center_repository.find_by_id_with_details(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if not center.is_owner(subject.id):
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        center.relieve()

        return CenterResponseDto.from_entity(center, center.holds, center.walls, center.fees)

    @transactional()
    async def update(self,
                     session: AsyncSession,
                     subject: RequestUser,
                     center_id: str,
                     dto: CenterUpdateRequestDto):
        center = await self.center_repository.find_by_id_with_details(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if center.user_id is None:
            raise BadRequestException(
                ErrorCode.ROW_ALREADY_DETELED,
                "이미 삭제된 암장입니다."
            )

        if not center.is_owner(subject.id):
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        center.update(**dto.center.dict())

        holds = []
        await self.center_hold_repository.delete_by_center_id(session, center.id)
        if dto.hold_info is not None:
            hold_is_color = dto.hold_info.is_color
            holds = await self.center_hold_repository.save_all(
                session,
                [CenterHold(center=center, name=e.name, difficulty=e.difficulty, is_color=hold_is_color)
                 for e in dto.hold_info.hold_list or []])

        await self.center_wall_repository.delete_by_center_id(session, center.id)
        walls = await self.center_wall_repository.save_all(
            session,
            [CenterWall(center=center, name=e.name, type=e.wall_type.value)
             for e in dto.wall_list or []])

        return CenterResponseDto.from_entity(entity=center, holds=holds, walls=walls)

    @transactional(read_only=True)
    async def find_center_fees(self,
                               session: AsyncSession,
                               subject: RequestUser,
                               center_id: str):
        center = await self.center_repository.find_by_id_with_details(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if not center.is_owner(subject.id):
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        return CenterFeeDetailResponseDto.from_entity(entity=center, fees=center.fees)

    @transactional()
    async def update_center_fees(self,
                                 session: AsyncSession,
                                 subject: RequestUser,
                                 center_id: str,
                                 dto: CenterFeeDetailRequestDto):
        center = await self.center_repository.find_by_id_with_details(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if not center.is_owner(subject.id):
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        prev_fees = {fee.id: fee for fee in center.fees}
        updated_fees = {fee.center_fee_id: fee for fee in dto.center_fee if fee.center_fee_id is not None}

        fees = []
        for fee_dto in dto.center_fee:
            if fee_dto.center_fee_id is None:
                fee = await self.center_fee_repository.save(session,
                                                            CenterFee.of(center_id=center_id, **fee_dto.dict()))
                fees.append(fee)
            else:
                fee = prev_fees.get(fee_dto.center_fee_id)
                if fee is not None:
                    fee.update(**fee_dto.dict())
                    fees.append(fee)

        for fee in center.fees:
            if fee.id not in updated_fees:
                fee.delete()

        center.update_fee_image(dto.fee_img)

        return CenterFeeDetailResponseDto.from_entity(entity=center, fees=fees)


    @transactional(read_only=True)
    async def find_schedules_by_center(self,
                                 session: AsyncSession,
                                 subject: RequestUser,
                                 center_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if not center.is_owner(subject.id):
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        schedules = await self.center_schedule_repository.find_by_center(session, center_id)
        return [ScheduleBriefResponseDto.from_entity(schedule) for schedule in schedules]

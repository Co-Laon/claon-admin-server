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
    CenterCreateRequestDto, CenterUpdateRequestDto, CenterFeeDetailResponseDto, CenterFeeResponseDto, \
    CenterFeeDetailRequestDto
from claon_admin.schema.center import CenterRepository, CenterHoldRepository, CenterWallRepository, CenterFeeImage, \
    CenterFeeRepository, CenterHold, CenterWall, CenterFee, CenterApprovedFileRepository, Center, CenterApprovedFile


class CenterService:
    def __init__(self,
                 center_repository: CenterRepository,
                 center_hold_repository: CenterHoldRepository,
                 center_wall_repository: CenterWallRepository,
                 center_fee_repository: CenterFeeRepository,
                 center_approved_file_repository: CenterApprovedFileRepository):
        self.center_repository = center_repository
        self.center_hold_repository = center_hold_repository
        self.center_wall_repository = center_wall_repository
        self.center_fee_repository = center_fee_repository
        self.center_approved_file_repository = center_approved_file_repository

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
    async def delete_center_fee(self,
                                session: AsyncSession,
                                subject: RequestUser,
                                center_id: str,
                                center_fee_id: str):
        center = await self.center_repository.find_by_id_with_details(session=session, center_id=center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "해당 암장이 존재하지 않습니다."
            )

        if not center.is_owner(user_id=subject.id):
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "암장 관리자가 아닙니다."
            )

        fee_ids = [fee.id for fee in center.fees]

        if center_fee_id not in fee_ids:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "암장에 해당 회원권 정보가 존재하지 않습니다."
            )

        center_fee = center.fees[fee_ids.index(center_fee_id)]

        if center_fee.is_deleted is True:
            raise BadRequestException(
                ErrorCode.ROW_ALREADY_DETELED,
                "이미 삭제된 회원권 입니다."
            )
        center_fee.delete()

        return CenterFeeResponseDto.from_entity(entity=center_fee)

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

        fees = [CenterFee(id=e.center_fee_id, center=center, center_id=center_id, name=e.name, fee_type=e.fee_type,
                          price=e.price, count=e.count, period=e.period, period_type=e.period_type)
                          for e in dto.center_fee]

        prev_fees = await self.center_fee_repository.find_all_by_center_id(session, center_id)
        deleted_fees = [e for e in prev_fees if e.id not in [k.id for k in fees]]
        [await self.center_fee_repository.delete(session, e) for e in deleted_fees]

        await self.center_fee_repository.upsert(session, fees)

        center.fee_img = [CenterFeeImage(e) for e in dto.fee_img]

        return CenterFeeDetailResponseDto.from_entity(entity=center, fees=fees)
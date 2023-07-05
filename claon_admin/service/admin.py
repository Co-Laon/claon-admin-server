from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import BadRequestException, ErrorCode, NotFoundException
from claon_admin.common.util.s3 import delete_file
from claon_admin.common.util.transaction import transactional
from claon_admin.model.admin import CenterResponseDto, LectorResponseDto
from claon_admin.common.enum import Role
from claon_admin.schema.center import CenterRepository, CenterApprovedFileRepository
from claon_admin.schema.user import LectorRepository, LectorApprovedFileRepository, UserRepository


class AdminService:
    def __init__(self,
                 user_repository: UserRepository,
                 lector_repository: LectorRepository,
                 lector_approved_file_repository: LectorApprovedFileRepository,
                 center_repository: CenterRepository,
                 center_approved_file_repository: CenterApprovedFileRepository):
        self.user_repository = user_repository
        self.lector_repository = lector_repository
        self.lector_approved_file_repository = lector_approved_file_repository
        self.center_repository = center_repository
        self.center_approved_file_repository = center_approved_file_repository

    @transactional()
    async def approve_lector(self, session: AsyncSession, lector_id: str):
        lector = await self.lector_repository.find_by_id_with_user(session, lector_id)
        if lector is None:
            raise BadRequestException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "선택한 강사의 정보가 존재하지 않습니다."
            )

        lector.approve()
        lector.user.update_role(Role.LECTOR)

        approved_files = await self.lector_approved_file_repository.find_all_by_lector_id(session, lector_id)
        await self.lector_approved_file_repository.delete_all_by_lector_id(session, lector_id)
        for file in approved_files:
            await delete_file(file.url)

        return LectorResponseDto.from_entity(lector, approved_files)

    @transactional()
    async def reject_lector(self, session: AsyncSession, lector_id: str):
        lector = await self.lector_repository.find_by_id(session, lector_id)
        if lector is None:
            raise BadRequestException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "선택한 강사의 정보가 존재하지 않습니다."
            )

        approved_files = await self.lector_approved_file_repository.find_all_by_lector_id(session, lector_id)
        for file in approved_files:
            await delete_file(file.url)

        return await self.lector_repository.delete(session, lector)

    @transactional()
    async def approve_center(self, session: AsyncSession, center_id: str):
        center = await self.center_repository.find_by_id_with_details(session, center_id)
        if center is None:
            raise NotFoundException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "선택한 센터의 정보가 존재하지 않습니다."
            )

        if await self.center_repository.exists_by_name_and_approved(session, center.name):
            raise BadRequestException(
                ErrorCode.DUPLICATED_NICKNAME,
                "이미 등록된 암장 이름 입니다."
            )

        center.approve()
        center.user.update_role(Role.CENTER_ADMIN)

        approved_files = await self.center_approved_file_repository.find_all_by_center_id(session, center_id)
        await self.center_approved_file_repository.delete_all_by_center_id(session, center_id)
        for file in approved_files:
            await delete_file(file.url)

        return CenterResponseDto.from_entity(center, approved_files)

    @transactional()
    async def reject_center(self, session: AsyncSession, center_id: str):
        center = await self.center_repository.find_by_id(session, center_id)
        if center is None:
            raise BadRequestException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "선택한 강사의 정보가 존재하지 않습니다."
            )

        approved_files = await self.center_approved_file_repository.find_all_by_center_id(session, center_id)
        for file in approved_files:
            await delete_file(file.url)

        await self.center_repository.delete(session, center)

    @transactional(read_only=True)
    async def get_unapproved_lectors(self, session: AsyncSession):
        return [LectorResponseDto.from_entity(
            lector,
            await self.lector_approved_file_repository.find_all_by_lector_id(session, lector.id)
        ) for lector in await self.lector_repository.find_all_by_approved_false(session)]

    @transactional(read_only=True)
    async def get_unapproved_centers(self, session: AsyncSession):
        return [CenterResponseDto.from_entity(
            center,
            await self.center_approved_file_repository.find_all_by_center_id(session, center.id)
        ) for center in await self.center_repository.find_all_by_approved_false(session)]

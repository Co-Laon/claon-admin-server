from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import BadRequestException, ErrorCode
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterResponseDto
from claon_admin.model.enum import Role
from claon_admin.model.user import LectorResponseDto
from claon_admin.schema.center import CenterRepository, CenterApprovedFileRepository
from claon_admin.schema.user import LectorRepository, LectorApprovedFileRepository


class AdminService:
    def __init__(self,
                 lector_repository: LectorRepository,
                 lector_approved_file_repository: LectorApprovedFileRepository,
                 center_repository: CenterRepository,
                 center_approved_file_repository: CenterApprovedFileRepository):
        self.lector_repository = lector_repository
        self.lector_approved_file_repository = lector_approved_file_repository
        self.center_repository = center_repository
        self.center_approved_file_repository = center_approved_file_repository

    async def approve_lector(self, lector_id: str, session: AsyncSession, subject: RequestUser):
        if subject.role != Role.ADMIN:
            raise BadRequestException(
                ErrorCode.NONE_ADMIN_ACCOUNT,
                "어드민 권한이 없습니다."
            )

        lector = await self.lector_repository.find_by_id(session, lector_id)

        if lector is None:
            raise BadRequestException(
                ErrorCode.ENTITY_NOT_FOUND,
                "선택한 강사의 정보가 존재하지 않습니다."
            )

        lector = await self.lector_repository.approve(session, lector)

        await self.lector_approved_file_repository.delete_all_by_lector_id(session, lector_id)
        return LectorResponseDto.from_entity(lector)

    async def reject_lector(self, lector_id: str, session: AsyncSession, subject: RequestUser):
        if subject.role != Role.ADMIN:
            raise BadRequestException(
                ErrorCode.NONE_ADMIN_ACCOUNT,
                "어드민 권한이 없습니다."
            )

        lector = await self.lector_repository.find_by_id(session, lector_id)

        if lector is None:
            raise BadRequestException(
                ErrorCode.ENTITY_NOT_FOUND,
                "선택한 강사의 정보가 존재하지 않습니다."
            )

        return await self.lector_repository.delete(session, lector)

    async def approve_center(self, center_id: str, session: AsyncSession, subject: RequestUser):
        if subject.role != Role.ADMIN:
            raise BadRequestException(
                ErrorCode.NONE_ADMIN_ACCOUNT,
                "어드민 권한이 없습니다."
            )

        center = await self.center_repository.find_by_id(session, center_id)

        if center is None:
            raise BadRequestException(
                ErrorCode.ENTITY_NOT_FOUND,
                "선택한 센터의 정보가 존재하지 않습니다."
            )

        center = await self.center_repository.approve(session, center)

        await self.center_approved_file_repository.delete_all_by_center_id(session, center_id)
        return CenterResponseDto.from_entity(center)

    async def reject_center(self, center_id: str, session: AsyncSession, subject: RequestUser):
        if subject.role != Role.ADMIN:
            raise BadRequestException(
                ErrorCode.NONE_ADMIN_ACCOUNT,
                "어드민 권한이 없습니다."
            )

        center = await self.center_repository.find_by_id(session, center_id)

        if center is None:
            raise BadRequestException(
                ErrorCode.ENTITY_NOT_FOUND,
                "선택한 강사의 정보가 존재하지 않습니다."
            )

        await self.center_repository.delete(session, center)

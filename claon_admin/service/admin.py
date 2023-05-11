from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import BadRequestException, ErrorCode, UnauthorizedException
from claon_admin.common.util.s3 import delete_file
from claon_admin.model.auth import RequestUser
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

    async def approve_lector(self, session: AsyncSession, subject: RequestUser, lector_id: str):
        if subject.role != Role.ADMIN:
            raise UnauthorizedException(
                ErrorCode.NONE_ADMIN_ACCOUNT,
                "어드민 권한이 없습니다."
            )

        lector = await self.lector_repository.find_by_id(session, lector_id)

        if lector is None:
            raise BadRequestException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "선택한 강사의 정보가 존재하지 않습니다."
            )

        lector = await self.lector_repository.approve(session, lector)
        await self.user_repository.update_role(session, lector.user, Role.LECTOR)

        approved_files = await self.lector_approved_file_repository.find_all_by_lector_id(session, lector_id)
        await self.lector_approved_file_repository.delete_all_by_lector_id(session, lector_id)
        [await delete_file(e.url) for e in approved_files]

        return LectorResponseDto.from_entity(lector, approved_files)

    async def reject_lector(self, session: AsyncSession, subject: RequestUser, lector_id: str):
        if subject.role != Role.ADMIN:
            raise UnauthorizedException(
                ErrorCode.NONE_ADMIN_ACCOUNT,
                "어드민 권한이 없습니다."
            )

        lector = await self.lector_repository.find_by_id(session, lector_id)

        if lector is None:
            raise BadRequestException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "선택한 강사의 정보가 존재하지 않습니다."
            )

        approved_files = await self.lector_approved_file_repository.find_all_by_lector_id(session, lector_id)
        [await delete_file(e.url) for e in approved_files]

        return await self.lector_repository.delete(session, lector)

    async def approve_center(self, session: AsyncSession, subject: RequestUser, center_id: str):
        if subject.role != Role.ADMIN:
            raise UnauthorizedException(
                ErrorCode.NONE_ADMIN_ACCOUNT,
                "어드민 권한이 없습니다."
            )

        center = await self.center_repository.find_by_id(session, center_id)

        if center is None:
            raise BadRequestException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "선택한 센터의 정보가 존재하지 않습니다."
            )

        center = await self.center_repository.approve(session, center)
        await self.user_repository.update_role(session, center.user, Role.CENTER_ADMIN)

        approved_files = await self.center_approved_file_repository.find_all_by_center_id(session, center_id)
        await self.center_approved_file_repository.delete_all_by_center_id(session, center_id)
        [await delete_file(e.url) for e in approved_files]

        return CenterResponseDto.from_entity(center, approved_files)

    async def reject_center(self, session: AsyncSession, subject: RequestUser, center_id: str):
        if subject.role != Role.ADMIN:
            raise UnauthorizedException(
                ErrorCode.NONE_ADMIN_ACCOUNT,
                "어드민 권한이 없습니다."
            )

        center = await self.center_repository.find_by_id(session, center_id)

        if center is None:
            raise BadRequestException(
                ErrorCode.DATA_DOES_NOT_EXIST,
                "선택한 강사의 정보가 존재하지 않습니다."
            )

        approved_files = await self.center_approved_file_repository.find_all_by_center_id(session, center_id)
        [await delete_file(e.url) for e in approved_files]
        await self.center_repository.delete(session, center)

    async def get_unapproved_lectors(self, session: AsyncSession, subject: RequestUser):
        if subject.role != Role.ADMIN:
            raise UnauthorizedException(ErrorCode.NONE_ADMIN_ACCOUNT, "어드민 권한이 없습니다.")

        lectors = await self.lector_repository.find_all_by_approved_false(session)
        result = list()

        for lector in lectors:
            lector_approved_file = await self.lector_approved_file_repository.find_all_by_lector_id(session, lector.id)
            result.append(LectorResponseDto.from_entity(lector, lector_approved_file))

        return result

    async def get_unapproved_centers(self, session: AsyncSession, subject: RequestUser):
        if subject.role != Role.ADMIN:
            raise UnauthorizedException(ErrorCode.NONE_ADMIN_ACCOUNT, "어드민 권한이 없습니다.")

        centers = await self.center_repository.find_all_by_approved_false(session)
        result = list()

        for center in centers:
            center_approved_file = await self.center_approved_file_repository.find_all_by_center_id(session, center.id)
            result.append(CenterResponseDto.from_entity(center, center_approved_file))

        return result

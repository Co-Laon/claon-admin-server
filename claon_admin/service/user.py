from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.model.user import IsDuplicatedNicknameResponseDto
from claon_admin.schema.user import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def check_nickname_duplication(self, session: AsyncSession, nickname: str):
        if await self.user_repository.exist_by_nickname(session, nickname):
            return IsDuplicatedNicknameResponseDto(is_duplicated=True)
        return IsDuplicatedNicknameResponseDto(is_duplicated=False)

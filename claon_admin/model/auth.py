from pydantic import BaseModel

from claon_admin.common.enum import Role


class RequestUser(BaseModel):
    id: str
    profile_image: str | None
    nickname: str | None
    sns: str
    email: str | None
    instagram_nickname: str | None
    role: Role | None

    def is_center_admin(self):
        return self.role == Role.CENTER_ADMIN

    def is_admin(self):
        return self.role == Role.ADMIN


class OAuthUserInfoDto(BaseModel):
    oauth_id: str
    sns_email: str

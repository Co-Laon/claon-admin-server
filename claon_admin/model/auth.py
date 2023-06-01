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


class OAuthUserInfoDto(BaseModel):
    oauth_id: str
    sns_email: str

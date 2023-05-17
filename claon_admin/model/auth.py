from typing import Optional

from pydantic import BaseModel

from claon_admin.common.enum import Role


class RequestUser(BaseModel):
    id: str
    profile_image: Optional[str]
    nickname: Optional[str]
    sns: str
    email: Optional[str]
    instagram_nickname: Optional[str]
    role: Optional[Role]


class OAuthUserInfoDto(BaseModel):
    oauth_id: str
    sns_email: str

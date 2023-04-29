from typing import Dict

import requests
from google.oauth2.id_token import verify_oauth2_token
from google.auth.transport.requests import Request

from claon_admin.common.error.exception import InternalServerException, ErrorCode
from claon_admin.config.config import conf
from claon_admin.model.auth import OAuthUserInfoDto
from claon_admin.common.enum import OAuthProvider


class UserInfoProvider:
    async def get_user_info(self, token: str):
        pass


class GoogleUserInfoProvider(UserInfoProvider):
    async def get_user_info(self, token: str):
        try:
            id_token = verify_oauth2_token(token, Request(), conf().GOOGLE_CLIENT_ID)

            if id_token is None:
                raise InternalServerException(
                    ErrorCode.INTERNAL_SERVER_ERROR,
                    "Failed to google login because of not existing id token"
                )

            return OAuthUserInfoDto(oauth_id=id_token['sub'], sns_email=id_token['email'])
        except Exception:
            raise InternalServerException(
                ErrorCode.INTERNAL_SERVER_ERROR,
                "Failed to get user information because of incorrect oauth token"
            )


class KakaoUserInfoProvider(UserInfoProvider):
    async def get_user_info(self, token: str):
        try:
            response: requests.Response = requests.get(
                url="https://kapi.kakao.com/v2/user/me",
                headers={
                    "Authorization": "Bearer " + token,
                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
                }
            )

            response.raise_for_status()

            user = response.json()
            return OAuthUserInfoDto(oauth_id=user['id'], sns_email=user['kakao_account']['email'])
        except Exception:
            raise InternalServerException(
                ErrorCode.INTERNAL_SERVER_ERROR,
                "Failed to Kakao login"
            )


class OAuthUserInfoProviderSupplier:
    def __init__(self,
                 google_user_info_provider: GoogleUserInfoProvider,
                 kakao_user_info_provider: KakaoUserInfoProvider):
        self.supplier: Dict[OAuthProvider, UserInfoProvider] = {
            OAuthProvider.GOOGLE: google_user_info_provider,
            OAuthProvider.KAKAO: kakao_user_info_provider
        }

    async def get_provider(self, provider: OAuthProvider):
        try:
            return self.supplier.get(provider)
        except Exception:
            raise InternalServerException(
                ErrorCode.INTERNAL_SERVER_ERROR,
                "Failed to get provider because of incorrect provider name"
            )

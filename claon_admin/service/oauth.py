from abc import ABC, abstractmethod
from typing import Dict

import requests
from google.oauth2.id_token import verify_oauth2_token
from google.auth.transport.requests import Request

from claon_admin.common.error.exception import InternalServerException, ErrorCode
from claon_admin.config.env import config
from claon_admin.model.auth import OAuthUserInfoDto
from claon_admin.common.enum import OAuthProvider

GOOGLE_CLIENT_ID = config.get("gcp.client-id")


class UserInfoProvider(ABC):
    @abstractmethod
    async def get_user_info(self, token: str):
        pass


class GoogleUserInfoProvider(UserInfoProvider):
    async def get_user_info(self, token: str):
        try:
            id_token = verify_oauth2_token(token, Request(), GOOGLE_CLIENT_ID)

            if id_token is None:
                raise InternalServerException(
                    ErrorCode.INTERNAL_SERVER_ERROR,
                    "Failed to google login because of not existing id token"
                )

            return OAuthUserInfoDto(oauth_id=id_token['sub'], sns_email=id_token['email'])
        except Exception as e:
            raise InternalServerException(
                ErrorCode.INTERNAL_SERVER_ERROR,
                "Failed to get user information because of incorrect oauth token"
            ) from e


class KakaoUserInfoProvider(UserInfoProvider):
    async def get_user_info(self, token: str):
        try:
            response: requests.Response = requests.get(
                url="https://kapi.kakao.com/v2/user/me",
                headers={
                    "Authorization": "Bearer " + token,
                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
                },
                timeout=5
            )

            response.raise_for_status()

            user = response.json()
            return OAuthUserInfoDto(oauth_id=user['id'], sns_email=user['kakao_account']['email'])
        except Exception as e:
            raise InternalServerException(
                ErrorCode.INTERNAL_SERVER_ERROR,
                "Failed to Kakao login"
            ) from e


class OAuthUserInfoProviderSupplier:
    def __init__(self):
        self.supplier: Dict[OAuthProvider, UserInfoProvider] = {
            OAuthProvider.GOOGLE: GoogleUserInfoProvider(),
            OAuthProvider.KAKAO: KakaoUserInfoProvider()
        }

    def get_provider(self, provider: OAuthProvider):
        try:
            return self.supplier.get(provider)
        except Exception as e:
            raise InternalServerException(
                ErrorCode.INTERNAL_SERVER_ERROR,
                "Failed to get provider because of incorrect provider name"
            ) from e

    async def get_user_info(self, provider: OAuthProvider, token: str):
        provider = self.get_provider(provider)

        return await provider.get_user_info(token)

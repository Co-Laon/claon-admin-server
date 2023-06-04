from unittest.mock import patch, AsyncMock

import pytest

from claon_admin.common.enum import Role, OAuthProvider
from claon_admin.service.oauth import OAuthUserInfoProviderSupplier, GoogleUserInfoProvider, KakaoUserInfoProvider
from claon_admin.model.auth import OAuthUserInfoDto
from claon_admin.model.user import SignInRequestDto
from claon_admin.schema.user import User
from claon_admin.service.user import UserService


@pytest.mark.describe("Test case for sign in")
class TestSignIn(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case: old user sign in with google")
    @patch("claon_admin.service.user.create_access_token")
    @patch("claon_admin.service.user.create_refresh_token")
    async def test_sign_in_with_google(
            self,
            mock_create_access_token,
            mock_create_refresh_token,
            mock_repo: dict,
            user_fixture: User,
            mock_supplier: OAuthUserInfoProviderSupplier,
            user_service: UserService
    ):
        # given
        user_fixture.role = Role.USER
        mock_repo["user"].find_by_oauth_id_and_sns.side_effect = [user_fixture]

        sign_in_request_dto = SignInRequestDto(id_token="test_id_token")
        provider_name = OAuthProvider.GOOGLE

        oauth_user_info_dto = OAuthUserInfoDto(oauth_id="oauth_id", sns_email="test_sns")
        mock_provider = AsyncMock(spec=GoogleUserInfoProvider)
        mock_provider.get_user_info.return_value = oauth_user_info_dto

        mock_supplier.get_provider.return_value = mock_provider

        mock_create_access_token.return_value = "test_access_token"
        mock_create_refresh_token.return_value = "test_refresh_token"

        # when
        result = await user_service.sign_in(provider_name, sign_in_request_dto)

        # then
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.is_signed_up is True

    @pytest.mark.asyncio
    @pytest.mark.it("Success case: new user sign in with google")
    @patch("claon_admin.service.user.create_access_token")
    @patch("claon_admin.service.user.create_refresh_token")
    async def test_sign_in_with_google_new_user(
            self,
            mock_create_access_token,
            mock_create_refresh_token,
            mock_repo: dict,
            user_fixture: User,
            mock_supplier: OAuthUserInfoProviderSupplier,
            user_service: UserService
    ):
        # given
        mock_repo["user"].find_by_oauth_id_and_sns.side_effect = [None]
        mock_repo["user"].save.side_effect = [user_fixture]

        sign_in_request_dto = SignInRequestDto(id_token="test_id_token")
        provider_name = OAuthProvider.GOOGLE

        oauth_user_info_dto = OAuthUserInfoDto(oauth_id="oauth_id", sns_email="test_sns")
        mock_provider = AsyncMock(spec=GoogleUserInfoProvider)
        mock_provider.get_user_info.return_value = oauth_user_info_dto

        mock_supplier.get_provider.return_value = mock_provider

        mock_create_access_token.return_value = "test_access_token"
        mock_create_refresh_token.return_value = "test_refresh_token"

        # when
        result = await user_service.sign_in(provider_name, sign_in_request_dto)

        # then
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.is_signed_up is False

    @pytest.mark.asyncio
    @pytest.mark.it("Success case: old user sign in with kakao")
    @patch("claon_admin.service.user.create_access_token")
    @patch("claon_admin.service.user.create_refresh_token")
    async def test_sign_in_with_kakao(
            self,
            mock_create_access_token,
            mock_create_refresh_token,
            mock_repo: dict,
            user_fixture: User,
            mock_supplier: OAuthUserInfoProviderSupplier,
            user_service: UserService
    ):
        # given
        user_fixture.role = Role.USER
        mock_repo["user"].find_by_oauth_id_and_sns.side_effect = [user_fixture]

        sign_in_request_dto = SignInRequestDto(id_token="test_id_token")
        provider_name = OAuthProvider.KAKAO

        oauth_user_info_dto = OAuthUserInfoDto(oauth_id="oauth_id", sns_email="test_sns")
        mock_provider = AsyncMock(spec=KakaoUserInfoProvider)
        mock_provider.get_user_info.return_value = oauth_user_info_dto

        mock_supplier.get_provider.return_value = mock_provider

        mock_create_access_token.return_value = "test_access_token"
        mock_create_refresh_token.return_value = "test_refresh_token"

        # when
        result = await user_service.sign_in(provider_name, sign_in_request_dto)

        # then
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.is_signed_up is True

    @pytest.mark.asyncio
    @pytest.mark.it("Success case: new user sign in with kakao")
    @patch("claon_admin.service.user.create_access_token")
    @patch("claon_admin.service.user.create_refresh_token")
    async def test_sign_in_with_kakao_new_user(
            self,
            mock_create_access_token,
            mock_create_refresh_token,
            mock_repo: dict,
            user_fixture: User,
            mock_supplier: OAuthUserInfoProviderSupplier,
            user_service: UserService
    ):
        # given
        mock_repo["user"].find_by_oauth_id_and_sns.side_effect = [None]
        mock_repo["user"].save.side_effect = [user_fixture]

        sign_in_request_dto = SignInRequestDto(id_token="test_id_token")
        provider_name = OAuthProvider.KAKAO

        oauth_user_info_dto = OAuthUserInfoDto(oauth_id="oauth_id", sns_email="test_sns")
        mock_provider = AsyncMock(spec=KakaoUserInfoProvider)
        mock_provider.get_user_info.return_value = oauth_user_info_dto

        mock_supplier.get_provider.return_value = mock_provider

        mock_create_access_token.return_value = "test_access_token"
        mock_create_refresh_token.return_value = "test_refresh_token"

        # when
        result = await user_service.sign_in(provider_name, sign_in_request_dto)

        # then
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.is_signed_up is False

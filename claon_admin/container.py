from dataclasses import asdict

from dependency_injector import containers, providers

from claon_admin.config.config import conf
from claon_admin.infra.provider import OAuthUserInfoProviderSupplier, GoogleUserInfoProvider, KakaoUserInfoProvider
from claon_admin.schema.center import CenterRepository, CenterApprovedFileRepository, CenterHoldRepository, \
    CenterWallRepository
from claon_admin.schema.conn import Database
from claon_admin.schema.user import UserRepository, LectorRepository, LectorApprovedFileRepository
from claon_admin.service.user import UserService

db = Database(db_url=asdict(conf())['DB_URL'])


class Container(containers.DeclarativeContainer):
    """ Repository """
    user_repository = providers.Factory(UserRepository)
    lector_repository = providers.Factory(LectorRepository)
    lector_approved_file_repository = providers.Factory(LectorApprovedFileRepository)
    center_repository = providers.Factory(CenterRepository)
    center_approved_file_repository = providers.Factory(CenterApprovedFileRepository)
    center_hold_repository = providers.Factory(CenterHoldRepository)
    center_wall_repository = providers.Factory(CenterWallRepository)

    """ Infrastructure """
    google_user_info_provider = providers.Factory(GoogleUserInfoProvider)
    kakao_user_info_provider = providers.Factory(KakaoUserInfoProvider)
    oauth_user_info_provider_supplier = providers.Factory(
        OAuthUserInfoProviderSupplier,
        google_user_info_provider=google_user_info_provider,
        kakao_user_info_provider=kakao_user_info_provider
    )

    """ Service """
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        lector_repository=lector_repository,
        lector_approved_file_repository=lector_approved_file_repository,
        center_repository=center_repository,
        center_approved_file_repository=center_approved_file_repository,
        center_hold_repository=center_hold_repository,
        center_wall_repository=center_wall_repository,
        oauth_user_info_provider_supplier=oauth_user_info_provider_supplier
    )

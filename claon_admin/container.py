from dependency_injector import containers, providers

from claon_admin import config, router
from claon_admin.schema.center import CenterRepository, CenterApprovedFileRepository, CenterHoldRepository, \
    CenterWallRepository, CenterFeeRepository, ReviewRepository, ReviewAnswerRepository
from claon_admin.schema.post import PostRepository, PostCountHistoryRepository
from claon_admin.schema.user import UserRepository, LectorRepository, LectorApprovedFileRepository
from claon_admin.service.admin import AdminService
from claon_admin.service.center import CenterService
from claon_admin.service.oauth import OAuthUserInfoProviderSupplier, GoogleUserInfoProvider, KakaoUserInfoProvider
from claon_admin.service.user import UserService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[config, router])

    """ Repository """
    user_repository = providers.Singleton(UserRepository)
    lector_repository = providers.Singleton(LectorRepository)
    lector_approved_file_repository = providers.Singleton(LectorApprovedFileRepository)
    center_repository = providers.Singleton(CenterRepository)
    center_approved_file_repository = providers.Singleton(CenterApprovedFileRepository)
    center_fee_repository = providers.Singleton(CenterFeeRepository)
    center_hold_repository = providers.Singleton(CenterHoldRepository)
    center_wall_repository = providers.Singleton(CenterWallRepository)
    post_repository = providers.Singleton(PostRepository)
    post_count_history_repository = providers.Singleton(PostCountHistoryRepository)
    review_repository = providers.Singleton(ReviewRepository)
    review_answer_repository = providers.Singleton(ReviewAnswerRepository)

    """ Infrastructure """
    google_user_info_provider = providers.Singleton(GoogleUserInfoProvider)
    kakao_user_info_provider = providers.Singleton(KakaoUserInfoProvider)
    oauth_user_info_provider_supplier = providers.Singleton(
        OAuthUserInfoProviderSupplier,
        google_user_info_provider=google_user_info_provider,
        kakao_user_info_provider=kakao_user_info_provider
    )

    """ Service """
    user_service = providers.Singleton(
        UserService,
        user_repository=user_repository,
        lector_repository=lector_repository,
        lector_approved_file_repository=lector_approved_file_repository,
        center_repository=center_repository,
        center_approved_file_repository=center_approved_file_repository,
        center_fee_repository=center_fee_repository,
        center_hold_repository=center_hold_repository,
        center_wall_repository=center_wall_repository,
        oauth_user_info_provider_supplier=oauth_user_info_provider_supplier
    )

    admin_service = providers.Singleton(
        AdminService,
        user_repository=user_repository,
        lector_repository=lector_repository,
        lector_approved_file_repository=lector_approved_file_repository,
        center_repository=center_repository,
        center_approved_file_repository=center_approved_file_repository
    )

    center_service = providers.Singleton(
        CenterService,
        center_repository=center_repository,
        post_repository=post_repository,
        post_count_history_repository=post_count_history_repository,
        review_repository=review_repository,
        review_answer_repository=review_answer_repository
    )

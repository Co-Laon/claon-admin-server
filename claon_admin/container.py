from dependency_injector import containers, providers

from claon_admin.common.util.pagination import PaginationFactory
from claon_admin.common.util.oauth import OAuthUserInfoProviderSupplier, GoogleUserInfoProvider, KakaoUserInfoProvider
from claon_admin.schema.center import CenterRepository, CenterApprovedFileRepository, CenterHoldRepository, \
    CenterWallRepository, CenterFeeRepository, ReviewRepository, ReviewAnswerRepository
from claon_admin.schema.post import PostRepository
from claon_admin.schema.user import UserRepository, LectorRepository, LectorApprovedFileRepository
from claon_admin.service.admin import AdminService
from claon_admin.service.center import CenterService
from claon_admin.service.user import UserService


class Container(containers.DeclarativeContainer):
    """ Repository """
    user_repository = providers.Factory(UserRepository)
    lector_repository = providers.Factory(LectorRepository)
    lector_approved_file_repository = providers.Factory(LectorApprovedFileRepository)
    center_repository = providers.Factory(CenterRepository)
    center_approved_file_repository = providers.Factory(CenterApprovedFileRepository)
    center_fee_repository = providers.Factory(CenterFeeRepository)
    center_hold_repository = providers.Factory(CenterHoldRepository)
    center_wall_repository = providers.Factory(CenterWallRepository)
    post_repository = providers.Factory(PostRepository)
    review_repository = providers.Factory(ReviewRepository)
    review_answer_repository = providers.Factory(ReviewAnswerRepository)
    pagination_factory = providers.Factory(PaginationFactory)

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
        center_fee_repository=center_fee_repository,
        center_hold_repository=center_hold_repository,
        center_wall_repository=center_wall_repository,
        oauth_user_info_provider_supplier=oauth_user_info_provider_supplier,
        pagination_factory=pagination_factory
    )

    admin_service = providers.Factory(
        AdminService,
        user_repository=user_repository,
        lector_repository=lector_repository,
        lector_approved_file_repository=lector_approved_file_repository,
        center_repository=center_repository,
        center_approved_file_repository=center_approved_file_repository
    )

    center_service = providers.Factory(
        CenterService,
        center_repository=center_repository,
        post_repository=post_repository,
        review_repository=review_repository,
        review_answer_repository=review_answer_repository,
        pagination_factory=pagination_factory
    )

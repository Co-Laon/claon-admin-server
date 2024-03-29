from dependency_injector import containers, providers

from claon_admin import router, job
from claon_admin.common import util
from claon_admin.schema.center import CenterRepository, CenterApprovedFileRepository, CenterHoldRepository, \
    CenterWallRepository, CenterFeeRepository, ReviewRepository, ReviewAnswerRepository, CenterScheduleRepository, \
    CenterScheduleMemberRepository
from claon_admin.schema.post import PostRepository, PostCountHistoryRepository
from claon_admin.schema.user import UserRepository, LectorRepository, LectorApprovedFileRepository
from claon_admin.service.admin import AdminService
from claon_admin.service.center import CenterService
from claon_admin.service.membership import MembershipService
from claon_admin.service.oauth import OAuthUserInfoProviderSupplier
from claon_admin.service.post import PostService
from claon_admin.service.review import ReviewService
from claon_admin.service.user import UserService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[util, router, job])

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
    center_schedule_repository = providers.Singleton(CenterScheduleRepository)
    center_schedule_member_repository = providers.Singleton(CenterScheduleMemberRepository)

    """ Service """
    oauth_user_info_provider_supplier = providers.Singleton(OAuthUserInfoProviderSupplier)

    user_service = providers.Singleton(
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
        user_repository=user_repository,
        center_repository=center_repository,
        center_fee_repository=center_fee_repository,
        center_hold_repository=center_hold_repository,
        center_wall_repository=center_wall_repository,
        center_approved_file_repository=center_approved_file_repository,
        center_schedule_repository=center_schedule_repository,
        center_schedule_member_repository=center_schedule_member_repository
    )

    post_service = providers.Singleton(
        PostService,
        center_repository=center_repository,
        post_repository=post_repository,
        post_count_history_repository=post_count_history_repository
    )

    review_service = providers.Singleton(
        ReviewService,
        center_repository=center_repository,
        review_repository=review_repository,
        review_answer_repository=review_answer_repository
    )

    membership_service = providers.Singleton(
        MembershipService
    )

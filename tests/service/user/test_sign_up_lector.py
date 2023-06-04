from datetime import date
from typing import List

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import BadRequestException, ErrorCode
from claon_admin.model.auth import RequestUser
from claon_admin.model.user import LectorRequestDto, LectorContestDto, LectorCertificateDto, LectorCareerDto, \
    UserProfileDto
from claon_admin.schema.user import Lector, LectorApprovedFile, User
from claon_admin.service.user import UserService


@pytest.mark.describe("Test case for sign up lector")
class TestSignUpLector(object):
    @pytest.fixture
    def lector_request_dto(self, user_fixture: User):
        yield LectorRequestDto(
            profile=UserProfileDto(
                profile_image=user_fixture.profile_img,
                nickname=user_fixture.nickname,
                email=user_fixture.email,
                instagram_nickname=user_fixture.instagram_name,
                role=user_fixture.role
            ),
            is_setter=True,
            contest_list=[
                LectorContestDto(
                    year=2021,
                    title='testtitle',
                    name='testname'
                )
            ],
            certificate_list=[
                LectorCertificateDto(
                    acquisition_date=date.fromisoformat('2012-10-15'),
                    rate=4,
                    name='testcertificate'
                )
            ],
            career_list=[
                LectorCareerDto(
                    start_date=date.fromisoformat('2016-01-01'),
                    end_date=date.fromisoformat('2020-01-01'),
                    name='testcareer'
                )
            ],
            proof_list=['https://test.com/test.pdf']
        )

    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_sign_up_lector(
            self,
            mock_repo: dict,
            user_service: UserService,
            lector_fixture: Lector,
            lector_approved_files_fixture: List[LectorApprovedFile],
            lector_request_dto: LectorRequestDto
    ):
        # given
        mock_repo["user"].exist_by_nickname.side_effect = [False]
        mock_repo["lector"].save.side_effect = [lector_fixture]
        mock_repo["lector_approved_file"].save_all.side_effect = [lector_approved_files_fixture]

        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)

        # when
        result = await user_service.sign_up_lector(request_user, lector_request_dto)

        # then
        assert result.is_setter == lector_request_dto.is_setter
        assert result.total_experience == 4
        assert result.contest_list == [
            LectorContestDto(
                year=e.year,
                title=e.title,
                name=e.name
            ) for e in lector_fixture.contest
        ]
        assert result.certificate_list == [
            LectorCertificateDto(
                acquisition_date=e.acquisition_date,
                rate=e.rate,
                name=e.name
            ) for e in lector_fixture.certificate
        ]
        assert result.career_list == [
            LectorCareerDto(
                start_date=e.start_date,
                end_date=e.end_date,
                name=e.name
            ) for e in lector_fixture.career
        ]
        assert result.approved is False

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: user nickname already exist")
    async def test_sign_up_lector_existing_nickname(
            self,
            mock_repo: dict,
            user_service: UserService,
            lector_request_dto: LectorRequestDto
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
        mock_repo["user"].exist_by_nickname.side_effect = [True]

        with pytest.raises(BadRequestException) as exception:
            # when
            await user_service.sign_up_lector(request_user, lector_request_dto)

        # then
        assert exception.value.code == ErrorCode.DUPLICATED_NICKNAME

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: user already sign up")
    async def test_sign_up_lector_already_sign_up(
            self,
            mock_repo: dict,
            user_service: UserService,
            lector_request_dto: LectorRequestDto
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.LECTOR)

        with pytest.raises(BadRequestException) as exception:
            # when
            await user_service.sign_up_lector(request_user, lector_request_dto)

        # then
        assert exception.value.code == ErrorCode.USER_ALREADY_SIGNED_UP

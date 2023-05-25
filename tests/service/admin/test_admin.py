from typing import List
from unittest.mock import patch

import pytest

from claon_admin.common.error.exception import BadRequestException, UnauthorizedException, ErrorCode
from claon_admin.model.auth import RequestUser
from claon_admin.common.enum import Role
from claon_admin.schema.center import Center, CenterApprovedFile
from claon_admin.schema.user import Lector, LectorApprovedFile
from claon_admin.service.admin import AdminService
from claon_admin.model.admin import CenterResponseDto, LectorResponseDto


@pytest.mark.asyncio
@patch("claon_admin.service.admin.delete_file")
async def test_approve_center(
        mock_delete_file,
        mock_repo: dict,
        admin_service: AdminService,
        mock_center: Center,
        mock_center_approved_files: List[CenterApprovedFile]
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
    center_id = mock_center.id

    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_center.approved = True
    mock_repo["center"].approve.side_effect = [mock_center]
    mock_repo["center"].exists_by_name_and_approved.side_effect = [False]
    mock_center.user.role = Role.CENTER_ADMIN
    mock_repo["user"].update_role.side_effect = [mock_center.user]
    mock_repo["center_approved_file"].find_all_by_center_id.side_effect = [mock_center_approved_files]
    mock_delete_file.return_value = None

    # when
    result = await admin_service.approve_center(None, request_user, center_id)

    # then
    assert result.approved
    assert result.user_profile.role == Role.CENTER_ADMIN


@pytest.mark.asyncio
async def test_approve_center_with_non_admin(
        mock_repo: dict,
        admin_service: AdminService,
        mock_center: Center
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
    center_id = mock_center.id

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await admin_service.approve_center(None, request_user, center_id)

    # then
    assert exception.value.code == ErrorCode.NONE_ADMIN_ACCOUNT


@pytest.mark.asyncio
async def test_approve_not_existing_center(
        mock_repo: dict,
        admin_service: AdminService
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
    center_id = "not_existing_id"

    mock_repo["center"].find_by_id.side_effect = [None]

    with pytest.raises(BadRequestException) as exception:
        # when
        await admin_service.approve_center(None, request_user, center_id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_approve_duplicated_center_name(
        mock_repo: dict,
        admin_service: AdminService,
        mock_center: Center
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
    center_id = mock_center.id

    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["center"].exists_by_name_and_approved.side_effect = [True]

    with pytest.raises(BadRequestException) as exception:
        # when
        await admin_service.approve_center(None, request_user, center_id)

    # then
    assert exception.value.code == ErrorCode.DUPLICATED_NICKNAME


@pytest.mark.asyncio
@patch("claon_admin.service.admin.delete_file")
async def test_approve_lector(
        mock_delete_file,
        mock_repo: dict,
        admin_service: AdminService,
        mock_lector: Lector,
        mock_lector_approved_files: List[LectorApprovedFile]
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
    lector_id = mock_lector.id

    mock_repo["lector"].find_by_id.side_effect = [mock_lector]
    mock_lector.approved = True
    mock_repo["lector"].approve.side_effect = [mock_lector]
    mock_lector.user.role = Role.LECTOR
    mock_repo["user"].update_role.side_effect = [mock_lector.user]
    mock_repo["lector_approved_file"].find_all_by_lector_id.side_effect = [mock_lector_approved_files]
    mock_delete_file.return_value = None

    # when
    result = await admin_service.approve_lector(None, request_user, lector_id)

    # then
    assert result.approved
    assert result.user_profile.role == Role.LECTOR


@pytest.mark.asyncio
async def test_approve_lector_with_non_admin(
        mock_repo: dict,
        admin_service: AdminService,
        mock_lector: Lector
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
    lector_id = mock_lector.id

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await admin_service.approve_lector(None, request_user, lector_id)

    # then
    assert exception.value.code == ErrorCode.NONE_ADMIN_ACCOUNT


@pytest.mark.asyncio
async def test_approve_not_existing_lector(
        mock_repo: dict,
        admin_service: AdminService,
        mock_lector: Lector
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
    lector_id = "not_existing_id"

    mock_repo["lector"].find_by_id.side_effect = [None]

    with pytest.raises(BadRequestException) as exception:
        # when
        await admin_service.approve_lector(None, request_user, lector_id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_reject_center(
        mock_repo: dict,
        admin_service: AdminService,
        mock_center: Center
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
    center_id = mock_center.id

    mock_repo["center"].find_by_id.side_effect = [mock_center]

    # when
    result = await admin_service.reject_center(None, request_user, center_id)

    # then
    assert result is None


@pytest.mark.asyncio
async def test_reject_center_with_non_admin(
        mock_repo: dict,
        admin_service: AdminService,
        mock_center: Center
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
    center_id = mock_center.id

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await admin_service.reject_center(None, request_user, center_id)

    # then
    assert exception.value.code == ErrorCode.NONE_ADMIN_ACCOUNT


@pytest.mark.asyncio
async def test_reject_not_existing_center(
        mock_repo: dict,
        admin_service: AdminService
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
    center_id = "not_existing_id"

    mock_repo["center"].find_by_id.side_effect = [None]

    with pytest.raises(BadRequestException) as exception:
        # when
        await admin_service.reject_center(None, request_user, center_id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_reject_lector(
        mock_repo: dict,
        admin_service: AdminService,
        mock_lector: Lector
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
    lector_id = mock_lector.id

    mock_repo["lector"].find_by_id.side_effect = [mock_lector]
    mock_repo["lector"].delete.side_effect = [mock_lector]

    # when
    result = await admin_service.reject_lector(None, request_user, lector_id)

    # then
    assert result is mock_lector


@pytest.mark.asyncio
async def test_reject_lector_with_non_admin(
        mock_repo: dict,
        admin_service: AdminService,
        mock_lector: Lector
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
    lector_id = mock_lector.id

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await admin_service.reject_lector(None, request_user, lector_id)

    # then
    assert exception.value.code == ErrorCode.NONE_ADMIN_ACCOUNT


@pytest.mark.asyncio
async def test_reject_not_existing_lector(
        mock_repo: dict,
        admin_service: AdminService
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
    lector_id = "not_existing_id"

    mock_repo["lector"].find_by_id.side_effect = [None]

    with pytest.raises(BadRequestException) as exception:
        # when
        await admin_service.reject_lector(None, request_user, lector_id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_get_unapproved_lectors(
        mock_repo: dict,
        admin_service: AdminService,
        mock_lector: Lector,
        mock_lector_approved_files: List[LectorApprovedFile]
):
    # given
    response = LectorResponseDto.from_entity(mock_lector, mock_lector_approved_files)
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
    mock_repo["lector"].find_all_by_approved_false.side_effect = [[mock_lector]]
    mock_repo["lector_approved_file"].find_all_by_lector_id.side_effect = [mock_lector_approved_files]

    # when
    result: List[LectorResponseDto] = await admin_service.get_unapproved_lectors(None, request_user)

    # then
    assert len(result) == 1
    assert mock_repo["lector"].find_all_by_approved_false.call_count == len(result)

    for lector in result:
        assert lector == response


@pytest.mark.asyncio
async def test_get_unapproved_lectors_with_non_admin(
        mock_repo: dict,
        admin_service: AdminService,
        mock_lector: Lector,
        mock_lector_approved_files: List[LectorApprovedFile]
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
    mock_repo["lector"].find_all_by_approved_false.side_effect = [[mock_lector]]
    mock_repo["lector_approved_file"].find_all_by_lector_id.side_effect = [mock_lector_approved_files]

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await admin_service.get_unapproved_lectors(None, request_user)

    # then
    assert exception.value.code == ErrorCode.NONE_ADMIN_ACCOUNT


@pytest.mark.asyncio
async def test_get_unapproved_centers(
        mock_repo: dict,
        admin_service: AdminService,
        mock_center: Center,
        mock_center_approved_files: List[CenterApprovedFile]
):
    # given
    response = CenterResponseDto.from_entity(mock_center, mock_center_approved_files)
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
    mock_repo["center"].find_all_by_approved_false.side_effect = [[mock_center]]
    mock_repo["center_approved_file"].find_all_by_center_id.side_effect = [mock_center_approved_files]

    # when
    result: List[CenterResponseDto] = await admin_service.get_unapproved_centers(None, request_user)

    # then
    assert len(result) == 1
    assert mock_repo["center"].find_all_by_approved_false.call_count == len(result)

    for center in result:
        assert center == response


@pytest.mark.asyncio
async def test_get_unapproved_centers_with_non_admin(
        mock_repo: dict,
        admin_service: AdminService,
        mock_center: Center,
        mock_center_approved_files: List[CenterApprovedFile]
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
    mock_repo["center"].find_all_by_approved_false.side_effect = [[mock_center]]
    mock_repo["center_approved_file"].find_all_by_center_id.side_effect = [mock_center_approved_files]

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await admin_service.get_unapproved_centers(None, request_user)

    # then
    assert exception.value.code == ErrorCode.NONE_ADMIN_ACCOUNT

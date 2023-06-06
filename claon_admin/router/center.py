from datetime import date
from typing import List

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_pagination import Params
from fastapi_utils.cbv import cbv

from claon_admin.common.util.auth import CurrentUser
from claon_admin.common.util.pagination import Pagination
from claon_admin.container import Container
from claon_admin.model.center import CenterNameResponseDto, CenterResponseDto, CenterUpdateRequestDto, \
    CenterBriefResponseDto, CenterRequestDto
from claon_admin.common.enum import CenterUploadPurpose
from claon_admin.model.file import UploadFileResponseDto
from claon_admin.model.post import PostResponseDto, PostSummaryResponseDto, PostCommentResponseDto, PostBriefResponseDto
from claon_admin.model.review import ReviewSummaryResponseDto, ReviewAnswerResponseDto, ReviewAnswerRequestDto, \
    ReviewBriefResponseDto
from claon_admin.service.center import CenterService

router = APIRouter()


@cbv(router)
class CenterRouter:
    @inject
    def __init__(self,
                 center_service: CenterService = Depends(Provide[Container.center_service])):
        self.center_service = center_service

    @router.get('/name/{name}', response_model=List[CenterNameResponseDto])
    async def get_name(self,
                       name: str):
        return await self.center_service.find_centers_by_name(name=name)

    @router.get('/{center_id}', response_model=CenterResponseDto)
    async def find_by_id(self,
                         subject: CurrentUser,
                         center_id: str):
        return await self.center_service.find_by_id(subject=subject, center_id=center_id)

    @router.post('/{purpose}/file', response_model=UploadFileResponseDto)
    async def upload(self,
                     subject: CurrentUser,
                     purpose: CenterUploadPurpose,
                     file: UploadFile = File(...)):
        return await self.center_service.upload_file(purpose, file)

    @router.get('/', response_model=Pagination[CenterBriefResponseDto])
    async def find_centers(self,
                           subject: CurrentUser,
                           params: Params = Depends()):
        return await self.center_service.find_centers(params=params, subject=subject)

    @router.post('/', response_model=CenterResponseDto)
    async def create(self,
                     dto: CenterRequestDto):
        pass

    @router.put('/{center_id}', response_model=CenterResponseDto)
    async def update(self,
                     center_id: str,
                     request_dto: CenterUpdateRequestDto):
        pass

    @router.delete('/{center_id}', response_model=CenterResponseDto)
    async def delete(self,
                     subject: CurrentUser,
                     center_id: str):
        return await self.center_service.delete(center_id=center_id, subject=subject)

    @router.get('/{center_id}/posts/{post_id}', response_model=PostResponseDto)
    async def find_post(self,
                        center_id: str,
                        post_id: str):
        pass

    @router.get('/{center_id}/posts/{post_id}/comments', response_model=PostCommentResponseDto)
    async def find_post_comment(self,
                                center_id: str,
                                post_id: str):
        pass

    @router.get('/{center_id}/posts', response_model=Pagination[PostBriefResponseDto])
    async def find_posts_by_center(self,
                                   subject: CurrentUser,
                                   center_id: str,
                                   start: date,
                                   end: date,
                                   hold_id: str | None = None,
                                   params: Params = Depends()):
        return await self.center_service.find_posts_by_center(
            subject=subject,
            params=params,
            hold_id=hold_id,
            center_id=center_id,
            start=start,
            end=end
        )

    @router.get('/{center_id}/reviews', response_model=Pagination[ReviewBriefResponseDto])
    async def find_reviews_by_center(self,
                                     subject: CurrentUser,
                                     center_id: str,
                                     start: date,
                                     end: date,
                                     tag: str | None = None,
                                     is_answered: bool | None = None,
                                     params: Params = Depends()):
        return await self.center_service.find_reviews_by_center(
            subject=subject,
            params=params,
            center_id=center_id,
            start=start,
            end=end,
            tag=tag,
            is_answered=is_answered
        )

    @router.get('/{center_id}/posts/summary', response_model=PostSummaryResponseDto)
    async def find_posts_summary_by_center(self,
                                           subject: CurrentUser,
                                           center_id: str):
        return await self.center_service.find_posts_summary_by_center(subject, center_id)

    @router.get('/{center_id}/reviews/summary', response_model=ReviewSummaryResponseDto)
    async def find_reviews_summary_by_center(self,
                                             subject: CurrentUser,
                                             center_id: str):
        return await self.center_service.find_reviews_summary_by_center(subject, center_id)

    @router.post('/{center_id}/reviews/{review_id}', response_model=ReviewAnswerResponseDto)
    async def create_review_answer(self,
                                   subject: CurrentUser,
                                   request_dto: ReviewAnswerRequestDto,
                                   center_id: str,
                                   review_id: str):
        return await self.center_service.create_review_answer(subject, request_dto, center_id, review_id)

    @router.put('/{center_id}/reviews/{review_id}', response_model=ReviewAnswerResponseDto)
    async def update_review_answer(self,
                                   subject: CurrentUser,
                                   request_dto: ReviewAnswerRequestDto,
                                   center_id: str,
                                   review_id: str):
        return await self.center_service.update_review_answer(subject, request_dto, center_id, review_id)

    @router.delete('/{center_id}/reviews/{review_id}')
    async def delete_review_answer(self,
                                   subject: CurrentUser,
                                   center_id: str,
                                   review_id: str):
        return await self.center_service.delete_review_answer(subject, center_id, review_id)

from datetime import timedelta, date
from typing import List

import pandas as pd
from pydantic import BaseModel

from claon_admin.common.util.time import get_relative_time, get_weekday
from claon_admin.schema.center import Post, Center
from claon_admin.schema.post import PostCountHistory


class PostBriefResponseDto(BaseModel):
    post_id: str
    content: str
    image: str
    created_at: str
    user_id: str
    user_nickname: str
    user_profile_image: str

    @classmethod
    def from_entity(cls, entity: Post):
        return PostBriefResponseDto(
            post_id=entity.id,
            content=entity.content,
            image=entity.img[0].url,
            created_at=get_relative_time(entity.created_at),
            user_id=entity.user.id,
            user_nickname=entity.user.nickname,
            user_profile_image=entity.user.profile_img
        )


class PostCount(BaseModel):
    unit: str
    count: int


class PostSummaryResponseDto(BaseModel):
    center_id: str
    center_name: str
    count_today: int
    count_week: int
    count_month: int
    count_total: int
    count_per_day: List[PostCount]
    count_per_week: List[PostCount]

    @classmethod
    def from_entity(cls,
                    center: Center,
                    end_date: date,
                    count_total: int,
                    count_history_by_year: List[PostCountHistory]):
        if not count_history_by_year:
            return PostSummaryResponseDto(
                center_id=center.id,
                center_name=center.name,
                count_today=0,
                count_week=0,
                count_month=0,
                count_total=count_total,
                count_per_day=[],
                count_per_week=[]
            )

        count_by_month, count_by_week, count_by_day = cls.__count_history(end_date, count_history_by_year)
        data_per_day, data_per_week = cls.__get_data_per_period(end_date, count_history_by_year)

        return PostSummaryResponseDto(
            center_id=center.id,
            center_name=center.name,
            count_today=sum([history.count for history in count_by_day]),
            count_week=sum([history.count for history in count_by_week]),
            count_month=sum([history.count for history in count_by_month]),
            count_total=count_total,
            count_per_day=[PostCount(unit=get_weekday(day), count=data_per_day[day])
                           for day in data_per_day],
            count_per_week=[PostCount(unit=week.strftime("%Y-%m-%d"), count=data_per_week[week])
                            for week in data_per_week]
        )

    @classmethod
    def __count_history(cls, standard_date: date, history_list: List[PostCountHistory]):
        count_by_month = list(filter(lambda x: standard_date - timedelta(days=4 * 7) <= x.reg_date < standard_date,
                                     history_list))
        count_by_week = list(filter(lambda x: standard_date - timedelta(days=7) <= x.reg_date < standard_date,
                                    count_by_month))
        count_by_day = list(filter(lambda x: standard_date - timedelta(days=1) <= x.reg_date < standard_date,
                                   count_by_week))

        return count_by_month, count_by_week, count_by_day

    @classmethod
    def __get_data_per_period(cls, end_date: date, history_list: List[PostCountHistory]):
        start_date = history_list[0].reg_date

        data = []
        for history in history_list:
            data.append({
                'reg_date': history.reg_date,
                'count': history.count
            })

        data_default = pd.DataFrame(pd.date_range(start_date, end_date - timedelta(days=1), freq="D"),
                                    columns=["reg_date"]).fillna(0)
        data_per_week = pd.DataFrame(data)
        data_per_week.reg_date = data_per_week.reg_date.astype("datetime64[ns]")
        data_per_week = pd.merge(data_default, data_per_week, on="reg_date", how="left").fillna(0).set_index("reg_date")
        data_per_day = data_per_week.iloc[-7:].T.to_dict("records")[0]
        data_per_week = data_per_week.resample("W")["count"].sum().to_frame()

        if end_date.weekday() > 0:
            data_per_week = data_per_week[0:-1]

        data_per_week = data_per_week.T.to_dict("records")[0]

        return data_per_day, data_per_week


class PostCommentResponseDto(BaseModel):
    user_id: str
    user_nickname: str
    user_profile_image: str
    created_at: str
    content: str
    child_count: int


class ClimbingHistoryDto(BaseModel):
    hold_id: str
    image: str
    count: int


class PostResponseDto(BaseModel):
    post_id: str
    content: str
    images: List[str]
    like_count: int
    climbing_history: List[ClimbingHistoryDto]
    created_at: str
    user_id: str
    user_nickname: str
    user_profile_image: str

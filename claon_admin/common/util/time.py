from datetime import datetime, date

from claon_admin.common.consts import TIME_ZONE_KST


def now():
    return datetime.now(TIME_ZONE_KST).replace(tzinfo=None)


def get_relative_time(time: datetime = datetime.now(TIME_ZONE_KST)):
    min_in_sec = 60
    hour_in_sec = 60 * min_in_sec
    day_in_sec = 24 * hour_in_sec
    week_in_sec = 7 * day_in_sec
    month_in_sec = 4 * week_in_sec

    diff = now() - time

    if diff.total_seconds() <= 0:
        return "방금 전"
    elif diff.total_seconds() < min_in_sec:
        return str(int(diff.total_seconds())) + "초 전"
    elif diff.total_seconds() < hour_in_sec:
        return str(diff.total_seconds() // min_in_sec) + "분 전"
    elif diff.total_seconds() < day_in_sec:
        return str(diff.total_seconds() // hour_in_sec) + "시간 전"
    elif diff.total_seconds() < week_in_sec:
        return str(diff.total_seconds() // day_in_sec) + "일 전"
    elif diff.total_seconds() < month_in_sec:
        return str(diff.total_seconds() // week_in_sec) + "주 전"
    else:
        return time.strftime("%Y-%m-%d")


def get_weekday(day: date):
    days = ["월", "화", "수", "목", "금", "토", "일"]
    return days[day.weekday()]

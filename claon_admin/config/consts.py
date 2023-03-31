from pytz import timezone

from claon_admin.config.config import config

TIME_ZONE_KST = timezone("Asia/Seoul")

KOR_BEGIN_CODE = 0xAC00
KOR_END_CODE = 0xD7AF

SESSION_SECRET_KEY = config.get("SESSION", "SECRET_KEY")

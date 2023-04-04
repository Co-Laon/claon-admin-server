from pytz import timezone

from claon_admin.config.config import config

TIME_ZONE_KST = timezone("Asia/Seoul")

KOR_BEGIN_CODE = 0xAC00
KOR_END_CODE = 0xD7AF

SESSION_SECRET_KEY = config.get("SESSION", "SECRET_KEY")

AWS_ACCESS_KEY_ID = config.get("AWS", "AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config.get("AWS", "AWS_SECRET_ACCESS_KEY")
REGION_NAME = config.get("AWS", "REGION_NAME")

BUCKET = config.get("S3", "BUCKET")
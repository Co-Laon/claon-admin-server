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

# JWT
JWT_ALGORITHM = config.get("JWT", "ALGORITHM")
JWT_SECRET_KEY = config.get("JWT", "JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = config.get("JWT", "JWT_REFRESH_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config.get("JWT", "ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(config.get("JWT", "REFRESH_TOKEN_EXPIRE_MINUTES"))

import mimetypes
import os
import uuid
from datetime import datetime
from tempfile import NamedTemporaryFile

from fastapi import UploadFile

from claon_admin.common.error.exception import InternalServerException, ErrorCode
from claon_admin.config.env import config
from claon_admin.config.log import logger
from claon_admin.config.s3 import s3

AWS_S3_BUCKET = config.get("aws.s3.bucket")
AWS_REGION = config.get("aws.region")


async def upload_file(file: UploadFile, domain: str, purpose: str):
    file_extension = file.filename.split('.')[-1]
    key_name = os.path.join(domain, purpose, str(datetime.now().date()), str(uuid.uuid4()) + '.' + file_extension)

    try:
        with NamedTemporaryFile() as temp_file:
            temp_file.write(await file.read())
            temp_file.seek(0)
            s3.upload_fileobj(
                temp_file,
                AWS_S3_BUCKET,
                key_name,
                ExtraArgs={"ContentType": mimetypes.guess_type(f"{file.filename}")[0], "ACL": "public-read"}
            )

            return os.path.join(
                "https://" + AWS_S3_BUCKET + ".s3." + AWS_REGION + ".amazonaws.com", key_name)
    except Exception as e:
        raise InternalServerException(ErrorCode.INTERNAL_SERVER_ERROR, "S3 객체 업로드를 실패했습니다.") from e


async def delete_file(url: str):
    prefix = "https://" + AWS_S3_BUCKET + ".s3." + AWS_REGION + ".amazonaws.com"
    key_name = url.replace(prefix, "")[1:]

    try:
        s3.delete_object(Bucket=AWS_S3_BUCKET, Key=key_name)
    except Exception:
        logger.error("S3 객체 삭제를 실패했습니다. url: %s", url)

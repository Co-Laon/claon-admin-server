import mimetypes
import os
import uuid
from datetime import datetime
from tempfile import NamedTemporaryFile

import boto3
from fastapi import UploadFile

from claon_admin.common.error.exception import InternalServerException, ErrorCode
from claon_admin.config.consts import AWS_ACCESS_KEY_ID
from claon_admin.config.consts import AWS_SECRET_ACCESS_KEY
from claon_admin.config.consts import BUCKET
from claon_admin.config.consts import REGION_NAME

client_s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME
)


async def upload_file(file: UploadFile, domain: str, purpose: str):
    file_extension = file.filename.split('.')[-1]
    key_name = os.path.join(domain, purpose, str(datetime.now().date()), str(uuid.uuid4()) + '.' + file_extension)

    try:
        with NamedTemporaryFile() as temp_file:
            temp_file.write(await file.read())
            temp_file.seek(0)
            client_s3.upload_fileobj(
                temp_file,
                BUCKET,
                key_name,
                ExtraArgs={"ContentType": mimetypes.guess_type(f"{file.filename}")[0], "ACL": "public-read"}
            )

            return os.path.join("https://" + BUCKET + ".s3." + REGION_NAME + ".amazonaws.com", key_name)
    except Exception:
        raise InternalServerException(ErrorCode.INTERNAL_SERVER_ERROR, "S3 객체 업로드를 실패했습니다.")

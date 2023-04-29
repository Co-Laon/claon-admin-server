import boto3

from claon_admin.config.config import conf


class S3Client:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )


s3 = None
if conf().AWS_ENABLE:
    s3 = S3Client(
        aws_access_key_id=conf().AWS_ACCESS_KEY_ID,
        aws_secret_access_key=conf().AWS_SECRET_ACCESS_KEY,
        region_name=conf().REGION_NAME,
    ).client

import boto3

from claon_admin.config.env import config

AWS_ENABLE = config.get("aws.enable")
AWS_ACCESS_KEY = config.get("aws.access-key")
AWS_SECRET_KEY = config.get("aws.secret-key")
AWS_REGION = config.get("aws.region")


class S3Client:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )


s3 = None
if AWS_ENABLE:
    s3 = S3Client(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    ).client

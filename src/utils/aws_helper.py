import os
import boto3

from urllib.parse import urlparse, parse_qs

# Initialize Boto3 clients and a cache for secrets/parameters
session = boto3.session.Session()
ssm_client = session.client('ssm')
secrets_client = session.client('secretsmanager')


def get_ssm_parameter(name: str, with_decryption: bool = True) -> str:
    """Fetches a parameter from AWS SSM Parameter Store, using a cache."""
    environment = os.environ.get('ENVIRONMENT', 'dev')
    full_name = f"/pharaoh/{environment}/{name}"
    response = ssm_client.get_parameter(Name=full_name, WithDecryption=with_decryption)

    value = response['Parameter']['Value']
    return value


def get_secret(name: str) -> dict:
    """Fetches a secret from AWS Secrets Manager, using a cache."""
    environment = os.environ.get('ENVIRONMENT', 'dev')
    full_name = f"/pharaoh/{environment}/{name}"

    response = secrets_client.get_secret_value(SecretId=full_name)

    secret_string = response['SecretString']
    return secret_string


def put_image(key: str, png_bytes) -> str:
    s3 = boto3.client("s3", config=boto3.session.Config(s3={'addressing_style': 'virtual'}, signature_version='s3v4'))
    bucket_name = os.environ.get('IMAGE_BUCKET_NAME', 'pharaoh-dev-test')
    s3.put_object(Bucket=bucket_name, Key=key, Body=png_bytes, ContentType="image/png")
    presigned_url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket_name, "Key": key},
        ExpiresIn=3600,  # 1 小時
    )
    return presigned_url


def is_s3_presigned_url(text: str) -> bool:
    try:
        parsed = urlparse(text)
        if parsed.scheme not in {"http", "https"}:
            return False
        qs = parse_qs(parsed.query)
        return all(k in qs for k in ["X-Amz-Algorithm", "X-Amz-Credential", "X-Amz-Signature"])
    except Exception:
        return False

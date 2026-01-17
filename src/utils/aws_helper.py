import os
import boto3

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

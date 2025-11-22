import json

from pymongo import MongoClient
from utils.aws_helper import get_ssm_parameter, get_secret


def get_mongo_client() -> MongoClient:
    try:
        connection_string_template = get_ssm_parameter("mongodb/coonnect-str")

        credentials_string = get_secret("mongodb/credentials")
        credentials = json.loads(credentials_string)
        username = credentials['username']
        password = credentials['password']

        full_connection_string = connection_string_template.replace("<username>", username).replace("<password>", password)
        
        return MongoClient(full_connection_string)
    except Exception as e:
        raise e

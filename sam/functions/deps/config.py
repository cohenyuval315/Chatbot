import os

def get_aws_config():
    if os.getenv("STAGE") == "Prod":
        pass
    if os.getenv("STAGE") == "Dev":
        pass
    endpoint_url = "http://172.17.0.2:4566"

    # endpoint_url = "http://localhost:4566"
    s3_region = "eu-west-3"
    s3_conf = {
        "aws_access_key_id":"test",
        "aws_secret_access_key":"test",
        "endpoint_url":endpoint_url,
        "region_name":s3_region,
        "verify":False
    }    
    return s3_conf



class SystemConfig:
    AWS_CONFIG = get_aws_config()
    STAGE = os.getenv("STAGE", "Dev")
    NAMESPACE = os.getenv("POWERTOOLS_METRICS_NAMESPACE", "ServerlessConversation")
    CORS = True
    BUCKET_NAME = "chatbot-bucket"
    BUCKET_NAME_PREFIX = "bucket"
    BUCKET_PER_MODEL = False
    DELETE_DYNAMO_DATA=False
    DELETE_DYNAMO_TABLES=False 
    OVERWRITE_MODELS = False

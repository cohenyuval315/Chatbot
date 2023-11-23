import os

def get_aws_config():
    if os.getenv("STAGE") == "Prod":
        pass
    if os.getenv("STAGE") == "Dev":
        pass
    endpoint_url = "http://172.17.0.2:4566"
    s3_region = "eu-west-3"
    s3_conf = {
        "aws_access_key_id":"test",
        "aws_secret_access_key":"test",
        "endpoint_url":endpoint_url,
        "region_name":s3_region,
        "verify":False
    }    
    return s3_conf

CONFIG = get_aws_config()
STAGE = os.getenv("STAGE", "Dev")
NAMESPACE = os.getenv("POWERTOOLS_METRICS_NAMESPACE", "ServerlessConversation")
MODEL_NAME = "google/flan-t5-small"
BUCKET_NAME = "test-bucket"
WARM_UP_KEY = "warm_up_status.json"
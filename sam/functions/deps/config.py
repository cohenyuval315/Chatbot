import os

def get_aws_config():
    if os.getenv("STAGE") == "Prod":
        pass
    if os.getenv("STAGE") == "Dev":
        pass
    endpoint_url = "http://172.17.0.5:4566"
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
MODEL_KEY="flan_t5_small"

MODEL_OPTIONS = [
    {
        "model":"google/flan-t5-small",
        "model_key":"flan_t5_small",
        "input_max_length": 1000,
    }
]

DELETE_DYNAMO_DATA=False
DELETE_DYNAMO_TABLES=False 

if DELETE_DYNAMO_DATA is False:
    DELETE_DYNAMO_TABLES = False



MODEL_AVAILABLE_OPTIONS = [0]
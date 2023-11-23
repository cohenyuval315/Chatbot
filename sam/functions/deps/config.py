import os
import dataclasses
from .config import *

@dataclasses.dataclass
class LLMConfiguration:
    model_name:str
    model_key:str
    max_length_input:int
    max_new_tokens:int
 
    def to_json(self):
        return {
            "model_name":self.model_name,
            "model_key":self.model_key,
            "max_length_input":self.max_length_input,
            "max_new_tokens":self.max_new_tokens
        }

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
WARM_UP_KEY = "warm_up_status.json"




BUCKET_NAME = "chatbot-bucket"
BUCKET_NAME_PREFIX = "bucket"
BUCKET_PER_MODEL = False

DELETE_DYNAMO_DATA=False
DELETE_DYNAMO_TABLES=False 

if DELETE_DYNAMO_DATA is False:
    DELETE_DYNAMO_TABLES = False



flan_t5 = LLMConfiguration(
    model_name="google/flan-t5-small",
    model_key="flan_t5_small",
    max_length_input=10000,
    max_new_tokens=1000
    )

MODEL_OPTIONS = [
    flan_t5
]

MODEL_AVAILABLE_OPTIONS = [0]
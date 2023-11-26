import os
import dataclasses
from .config import *
from typing import Optional
import enum

class TaskType(enum.Enum):
    DEFAULT = "default"
    QA = "QuestionAnswer"
    SUM = "summarization"


@dataclasses.dataclass
class LLMConfiguration:

    model_name:str
    model_key:str
    max_length_input:int
    max_new_tokens:Optional[int]
    model_link: Optional[str] = None
    tasks: Optional[list[TaskType]] = None
    trainable:bool = False

    # 
    max_length:int = 20
    min_length:int = 0 
    min_new_tokens:Optional[int] 
    max_time:Optional[float]
    early_stopping:Optional[str] = False 
 

    def to_json(self): 
        res =  {
            "model_name":self.model_name,
            "model_key":self.model_key,
            "max_length_input":self.max_length_input,
            "max_new_tokens":self.max_new_tokens,
            'trainable':self.trainable
        }
        if self.model_link:
            res['model_link'] = self.model_link
        if self.model_link:
            res['tasks'] = self.tasks            
        return res
    

    def to_user_json(self): # return to user
        res =  {
            "model_name":self.model_name,
            "model_key":self.model_key,
            "max_length_input":self.max_length_input,
            "max_new_tokens":self.max_new_tokens,
            'trainable':self.trainable
        }
        if self.model_link:
            res['model_link'] = self.model_link
        if self.model_link:
            res['tasks'] = self.tasks            
        return res
    
    

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


CORS = True


BUCKET_NAME = "chatbot-bucket"
BUCKET_NAME_PREFIX = "bucket"
BUCKET_PER_MODEL = False

DELETE_DYNAMO_DATA=False
DELETE_DYNAMO_TABLES=False 

if DELETE_DYNAMO_DATA is False:
    DELETE_DYNAMO_TABLES = False


tasks: Optional[list[TaskType]] = None
trainable:bool = False
 

flan_t5_small = LLMConfiguration(
    model_name="google/flan-t5-small",
    model_key="flan_t5_small",
    max_length_input=10000,
    max_new_tokens=1000,
    model_link="https://huggingface.co/google/flan-t5-small",
    tasks=[TaskType.DEFAULT,TaskType.QA,TaskType.SUM],
    trainable=False
    )

flan_t5_base = LLMConfiguration(
    model_name="google/flan-t5-base",
    model_key="flan_t5_base",
    max_length_input=10000,
    max_new_tokens=1000,
    model_link="https://huggingface.co/google/flan-t5-base",
    tasks=[TaskType.DEFAULT,TaskType.QA,TaskType.SUM],
    trainable=False
    )




MODEL_OPTIONS = [
    flan_t5_small,
    flan_t5_base
]

MODEL_AVAILABLE_OPTIONS_INDEXES = [0,1]
MODEL_AVAILABLE_OPTIONS = []
for model_option_index in MODEL_AVAILABLE_OPTIONS_INDEXES:
    MODEL_AVAILABLE_OPTIONS.append(MODEL_OPTIONS[model_option_index])


OVERWRITE_MODELS = False

COMPLETED_STATUS_INDICATOR = "COMPLETED"
ONGOING_STATUS_INDICATOR = "ONGOING"
FAIL_STATUS_INDICATOR = "FAILURE"
CLEAN_STATUS_INDICATOR= "CLEAN"
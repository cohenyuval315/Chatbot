from .globals import *
from .execptions import *

def make_lambda_response(statusCode:int,body:dict=None,headers:dict=None):
    cors_headers = {
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Origin": "*",
    }
    response = {
        "statusCode": statusCode,
        "isBase64Encoded": 'false',
    }
    if headers:
        cors_headers.update(headers)
        response['headers'] = cors_headers
    else:
        response['headers'] = cors_headers
    if body:
        response['body'] = body
    return response

def make_lambda_message_response(statusCode:int,message:str,headers:dict=None):
    return make_lambda_response(statusCode,{"message": message},headers)

def make_lambda_error_response(statusCode:int,error_message:str,headers:dict=None):
    return make_lambda_response(statusCode,{"error": error_message},headers)

def make_lambda_data_response(data:str,headers:dict=None):
    return make_lambda_response(200,{"data": data},headers)




def get_warm_up_key(model_key):
    return f"{model_key}/{WARM_UP_KEY}"

def get_warm_up_status(model_key):
    status = ONGOING_STATUS_INDICATOR    
    if BUCKET_PER_MODEL:
        bucket_name = get_model_bucket_name(get_model_by_key(model_key).model_name)
    else:
        bucket_name = BUCKET_NAME
    key = get_warm_up_key(model_key)
    response = s3.get_object(Bucket=bucket_name, Key=key)
    status = response["Body"].read().decode("utf-8")
    return status

def create_bucket(bucket_name):
    s3_region = "eu-west-3"
    response = s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': s3_region 
        }
    )
    return response
    
def clean_bucket(bucket_name):    
    objects = s3.list_objects_v2(Bucket=bucket_name).get('Contents', [])
    for obj in objects:
        s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
    return objects

def delete_bucket(bucket_name):
    res = s3.delete_bucket(Bucket=bucket_name)
    return res

def get_model(model_name):
    for option in MODEL_OPTIONS:
        if option.model_name == model_name:
            return option
    
def get_available_model(model_name):
    for model_option_index in MODEL_AVAILABLE_OPTIONS_INDEXES:
        if MODEL_OPTIONS[model_option_index].model_name == model_name:
            return MODEL_OPTIONS[model_option_index]
         
def get_available_models():
    return MODEL_AVAILABLE_OPTIONS

def get_model_bucket_name(model_name):
    if BUCKET_PER_MODEL is False:
        return BUCKET_NAME
    return f"{BUCKET_NAME_PREFIX}-{model_name}"

def get_models_buckets_names():
    if BUCKET_PER_MODEL is False:
        return BUCKET_NAME
    names = []
    for conf in get_available_models():
        names.append(get_model_bucket_name(conf.model_name))
    return names
    
def get_model_by_key(model_key):
    for option in MODEL_OPTIONS:
        if option.model_key == model_key:
            return option
  

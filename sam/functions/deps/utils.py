from botocore.exceptions import NoCredentialsError
from .logger import logger
from .globals import *
from .execptions import ModelNotFoundError,ModelNotAvailableError


def get_warm_up_key(model_key):
    return f"{model_key}/{WARM_UP_KEY}"


def get_warm_up_status(model_key):
    logger.debug("func:get_warm_up_status: get status")
    ongoing_status_indicator = "ongoing"
    status = ongoing_status_indicator    
    if BUCKET_PER_MODEL:
        bucket_name = get_model_bucket_name(get_model_by_key(model_key).model_name)
    else:
        bucket_name = BUCKET_NAME
    key = get_warm_up_key(model_key)
    logger.debug(key)
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        status = response["Body"].read().decode("utf-8")
    except s3.exceptions.NoSuchBucket:
        status = ongoing_status_indicator
        logger.error("no such bucket")
    except s3.exceptions.NoSuchKey:
        status = ongoing_status_indicator
        logger.error("no such key")
    return status


def create_bucket(bucket_name):
    logger.info(f"func:create_bucket: creating S3 Bucket '{bucket_name}'.")
    s3_region = "eu-west-3"
    try:
        response = s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': s3_region 
            }
        )
        logger.debug(response)
        logger.info(f"Bucket '{bucket_name}' created successfully.")
    except Exception as e:
        logger.error(f"Error creating bucket: {e}")    
        return bucket_name
    
def clean_bucket(bucket_name):
    logger.info(f"func:clean_bucket:cleaning S3 Bucket '{bucket_name}'.")
    try:
        objects = s3.list_objects_v2(Bucket=bucket_name).get('Contents', [])
        for obj in objects:
            res = s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
            logger.debug(res)
        logger.info(f"S3 Bucket '{bucket_name}' all objects deleted successfully.")
    except NoCredentialsError as e:
        logger.error(f"Error deleting S3 bucket: {e}")
    except Exception as e:
        logger.error(f"Error deleting S3 bucket: {e}")

def delete_bucket(bucket_name):
    logger.info(f"func:delete_bucket: deleting S3 Bucket '{bucket_name}'.")
    clean_bucket(bucket_name)
    try:
        res = s3.delete_bucket(Bucket=bucket_name)
        logger.debug(res)
        logger.info(f"S3 Bucket '{bucket_name}' deleted successfully.")
    except NoCredentialsError as e:
        logger.error(f"Error deleting bucket: {e}")
    except Exception as e:
        logger.error(f"Error deleting bucket: {e}")


def get_model(model_name):
    for option in MODEL_OPTIONS:
        if option.model_name == model_name:
            return option
    raise ModelNotFoundError    
    
def get_available_model(model_name):
    for model_option_index in MODEL_AVAILABLE_OPTIONS:
        if MODEL_OPTIONS[model_option_index].model_name == model_name:
            return MODEL_OPTIONS[model_option_index]
    if get_model(model_name):
        raise ModelNotAvailableError                
         
def get_available_models():
    models = []
    for model_option_index in MODEL_AVAILABLE_OPTIONS:
        models.append(MODEL_OPTIONS[model_option_index])
    return models

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
    raise ModelNotFoundError    
  
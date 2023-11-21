from botocore.exceptions import NoCredentialsError
from .logger import logger
from .globals import s3
from .config import BUCKET_NAME,WARM_UP_KEY


def get_warm_up_status():
    logger.debug("func:get_warm_up_status: get status")
    ongoing_status_indicator = "ongoing"
    status = ongoing_status_indicator    
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=WARM_UP_KEY)
        status = response["Body"].read().decode("utf-8")
    except s3.exceptions.NoSuchBucket:
        status = ongoing_status_indicator
    except s3.exceptions.NoSuchKey:
        status = ongoing_status_indicator
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




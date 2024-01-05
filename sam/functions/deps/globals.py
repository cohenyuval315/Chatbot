from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
)
import boto3
from .config import *
from .db_manager import DynamoDB
from .logger import logger

AWS_CONFIG = get_aws_config()

try:
    app = APIGatewayRestResolver()
    tracer = Tracer()
    metrics = Metrics(namespace=SystemConfig.NAMESPACE)
    s3 = boto3.client("s3",**SystemConfig.AWS_CONFIG)    
    dynamodb = boto3.resource('dynamodb',**SystemConfig.AWS_CONFIG)
    iam = boto3.client('iam',**SystemConfig.AWS_CONFIG)
    db_manager = DynamoDB(dynamodb)
    
except Exception as e:
    logger.error(e)



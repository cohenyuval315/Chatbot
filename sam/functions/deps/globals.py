from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
)
import boto3
from .config import *
from .db_manager import DynamoDB


app = APIGatewayRestResolver()
tracer = Tracer()
metrics = Metrics(namespace="ServerlessConversation")
s3 = boto3.client("s3",**CONFIG)    
dynamodb = boto3.resource('dynamodb',**CONFIG)
iam = boto3.client('iam',**CONFIG)

db_manager = DynamoDB(dynamodb)


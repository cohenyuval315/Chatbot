from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
)
import boto3
from .config import *
from .db_manager import DBManager
from .model_manager import ModelManager

app = APIGatewayRestResolver()
tracer = Tracer()
metrics = Metrics(namespace="ServerlessConversation")
s3 = boto3.client("s3",**CONFIG)    
dynamodb = boto3.resource('dynamodb',**CONFIG)
model_manager = ModelManager(s3,BUCKET_NAME,MODEL_NAME,WARM_UP_KEY)
db_manager = DBManager(dynamodb)
cors = True

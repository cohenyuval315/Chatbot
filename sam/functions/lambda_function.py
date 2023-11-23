from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    InternalServerError,
    NotFoundError,
    ServiceError,
    UnauthorizedError,
)
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
    Response,
    content_types,
    CORSConfig
)
import os 
import boto3
import transformers
import zipfile
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from transformers import T5Tokenizer, T5ForConditionalGeneration
import json
import shutil
import io
import botocore

import logging
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError,NoCredentialsError
import uuid
from datetime import datetime
from typing import Callable
import time

# def get_aws_config():
#     if os.getenv("STAGE") == "Prod":
#         pass
#     if os.getenv("STAGE") == "Dev":
#         pass
#     endpoint_url = "http://172.17.0.2:4566"
#     s3_region = "eu-west-3"
#     s3_conf = {
#         "aws_access_key_id":"test",
#         "aws_secret_access_key":"test",
#         "endpoint_url":endpoint_url,
#         "region_name":s3_region,
#         "verify":False
#     }    
#     return s3_conf

# def create_bucket(bucket_name):
#     logger.info(f"func:create_bucket: creating S3 Bucket '{bucket_name}'.")
#     s3_region = "eu-west-3"
#     try:
#         response = s3.create_bucket(
#             Bucket=bucket_name,
#             CreateBucketConfiguration={
#                 'LocationConstraint': s3_region 
#             }
#         )
#         logger.debug(response)
#         logger.info(f"Bucket '{bucket_name}' created successfully.")
#     except Exception as e:
#         logger.error(f"Error creating bucket: {e}")    
#         return bucket_name
    
# def clean_bucket(bucket_name):
#     logger.info(f"func:clean_bucket:cleaning S3 Bucket '{bucket_name}'.")
#     try:
#         objects = s3.list_objects_v2(Bucket=bucket_name).get('Contents', [])
#         for obj in objects:
#             res = s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
#             logger.debug(res)
#         logger.info(f"S3 Bucket '{bucket_name}' all objects deleted successfully.")
#     except NoCredentialsError as e:
#         logger.error(f"Error deleting S3 bucket: {e}")
#     except Exception as e:
#         logger.error(f"Error deleting S3 bucket: {e}")

# def delete_bucket(bucket_name):
#     logger.info(f"func:delete_bucket: deleting S3 Bucket '{bucket_name}'.")
#     clean_bucket(bucket_name)
#     try:
#         res = s3.delete_bucket(Bucket=bucket_name)
#         logger.debug(res)
#         logger.info(f"S3 Bucket '{bucket_name}' deleted successfully.")
#     except NoCredentialsError as e:
#         logger.error(f"Error deleting bucket: {e}")
#     except Exception as e:
#         logger.error(f"Error deleting bucket: {e}")


# class ModelManager:
#     model = None
#     tokenizer = None
    
#     def __init__(self,s3,bucket_name):
#         self.s3 = s3
#         self.s3_bucket = bucket_name
#         self.model_name = "google/flan-t5-small"
#         self.zip_key = "model_data.zip"
#         self.model_key = "model_weights"
#         self.tokenizer_key = "model_tokenizer_weights"

#         self.local_path = "/tmp/model/"
#         self.model_local_path = f"{self.local_path}model"
#         self.tokenizer_local_path = f"{self.local_path}tokenizer"

#         self.max_new_tokens = 1000
#         if ModelManager.model and ModelManager.tokenizer:
#             self.is_initialized = True
#         else:
#             self.is_initialized = False
#         self.max_length_input = 10000

#         self._temp_root = "/tmp"
#         self._temp_root_dir = f"{self._temp_root}/model"
#         self._temp_s3_model_path = f"{self._temp_root_dir}/model"
#         self._temp_s3_tokenizer_path =  f"{self._temp_root_dir}/tokenizer"
#         self.format = "zip"
#         self.compress_name = "model"

#         self.warm_up_key = "warm_up_status.json"
#         self.completed_status_indicator = "completed"
#         self.ongoing_status_indicator = "ongoing"
#         self.fail_status_indicator = "failure"
#         self.clean_status_indicator= "clean"
        

#     def initialize_model(self):
#         logger.info("func:initialize_model: Initialing Model")
#         if ModelManager.model:
#             logger.info("func:initialize_model: model already iniitialized")
#             return

#         if ModelManager.tokenizer:
#             logger.info("func:initialize_model: tokenizer already iniitialized")
#             return
#         try:
#             logger.info("func:initialize_model: get model zip")
#             res = self.s3.get_object(Bucket=self.s3_bucket, Key=self.zip_key)
#             logger.info("func:initialize_model: read model zip")
#             zip_data = res['Body'].read()
#             zip_buffer = io.BytesIO(zip_data)
#             logger.info("func:initialize_model: extract model zip")
#             with zipfile.ZipFile(zip_buffer,'r') as zip_ref:
#                 zip_ref.extractall(self.local_path)
#             logger.info("func:initialize_model: iniitializing model and tokenizer class instances")
#             ModelManager.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_local_path)
#             ModelManager.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_local_path)
#             self.is_initialized = True
#         except Exception as e:
#             logger.error("error in initialing model: %s",e)
    
#     def upload_model(self):
#         logger.info("func:upload_model: uploading model to s3...")
#         try:
#             self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=self.ongoing_status_indicator)
#             model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
#             tokenizer = AutoTokenizer.from_pretrained(self.model_name)
#             model.save_pretrained(self._temp_s3_model_path)
#             tokenizer.save_pretrained(self._temp_s3_tokenizer_path)
#             path = shutil.make_archive(self._temp_root + self.compress_name,self.format,root_dir=self._temp_root_dir)
#             self.s3.upload_file(Filename=path, Bucket=self.s3_bucket, Key=self.zip_key)
#             self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=self.completed_status_indicator)
#             res = {
#                 "status": self.completed_status_indicator
#             }
#             return res
#         except botocore.exceptions.ClientError as e:
#             logger.error(f"Error in upload_model: {e}")
#             res = {
#                 "err": str(e),
#             }
#             return res
#         except Exception as e:
#             logger.error(f"Error in upload_model: {e}")
#             self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=self.fail_status_indicator)
#             res = {
#                 "status": self.fail_status_indicator,
#             }
#             return res

#     def _handle_input(self,text_inputs):
#         logger.info("func:_handle_input:handle input")
#         model_input = '' 

#         if isinstance(text_inputs,list):
#             history_size = len(text_inputs)
#             if history_size > 1:
#                 history_sizes = reversed(text_inputs)
#                 acc = history_size
#                 prompt_history = []
#                 for s in history_sizes:
#                     if acc + len(s) > self.max_length_input:
#                         break
#                     acc += len(s)
#                     prompt_history.append(s)
#                 model_input = " ".join(reversed(prompt_history))
#             else:
#                 model_input = text_inputs[0]
#                 if len(model_input) > self.max_length_input:
#                     model_input =  model_input[-self.max_length_input:]

#         if isinstance(text_inputs,str):
#             model_input = text_inputs
#             if len(model_input) > self.max_length_input:
#                 model_input =  model_input[-self.max_length_input:]            

#         return model_input

#     def _prepare_model_input(self,text):
#         logger.info("func:_prepare_model_input:Prepare Model Input")
#         return text

#     def predict_title(self,text_input:str):
#         logger.info("func:predict_title: Generating title for chat by first prompt...")
#         title_prompt_input = self._handle_input(text_input)
#         title_prompt = f'please give a title for the following prompt "{title_prompt_input}"'
#         model_input = self._prepare_model_input(title_prompt)
#         res = self._predict(model_input)
#         logger.debug(res)
#         if isinstance(res, list):
#             res = " ".join(res)
#         if res is None:
#             res = ''
#         return res

#     def _predict(self,text_inputs,max_new_tokens=None):
#         logger.info("func:_predict: Predicting ...")
#         max_tokens = max_new_tokens if max_new_tokens else self.max_new_tokens
#         if not ModelManager.tokenizer:
#             logger.info("func:_predict: No Tokenizer ...")
#         if not ModelManager.model:
#             logger.info("func:_predict: No Model ...")
#         try:
#             inputs = ModelManager.tokenizer(text_inputs, return_tensors="pt")
#             outputs = ModelManager.model.generate(**inputs,max_new_tokens=max_tokens)
#             response = ModelManager.tokenizer.batch_decode(outputs, skip_special_tokens=True)
#             logger.info("func:_predict: successful prediction")
#             return response
#         except Exception as e:
#             logger.error(f"func:_predict: error in predicting: {e}")
#             logger.debug(inputs)
            
#     def predict_prompt(self,text_inputs,max_new_tokens=None):
#         logger.info("func:predict_prompt: Predicting Prompt...")
#         model_input = self._prepare_model_input(self._handle_input(text_inputs))
#         res = self._predict(model_input,max_new_tokens)
#         if isinstance(res, list):
#             res = " ".join(res)
#         if res is None:
#             res = ''
#         logger.debug(res)
#         return res

# class DBManager:
#     chats_table = None
#     chats_logs_table = None

#     def __init__(self,dynamodb) -> None:
#         self.dynamodb = dynamodb
#         self.chats_table_name = 'chats'
#         self.chats_logs_table_name = 'chats_logs'

#     def initilize_db(self):
#         DBManager.chats_table = self.get_table(self.chats_table_name)
#         DBManager.chats_logs_table = self.get_table(self.chats_logs_table_name)

#     def create_tables(self):
#         logger.info("creating tables")
#         self.create_table(
#             table_name=self.chats_table_name,
#             key_schema=[
#                 {'AttributeName': 'chat_id', 'KeyType': 'HASH'},
#             ],
#             attribute_definitions=[
#                 {'AttributeName': 'chat_id', 'AttributeType': 'S'},
#             ]
#         )
#         self.create_table(
#             table_name=self.chats_logs_table_name,
#             key_schema=[
#                 {'AttributeName': 'prompt_id', 'KeyType': 'HASH'},
#             ],
#             attribute_definitions=[
#                 {'AttributeName': 'prompt_id', 'AttributeType': 'S'},
#                 {'AttributeName': 'chat_id', 'AttributeType': 'S'},
#             ],
#                 GlobalSecondaryIndexes=[
#                     {
#                         'IndexName': 'chat_id_index',
#                         'KeySchema': [
#                             {'AttributeName': 'chat_id', 'KeyType': 'HASH'},
#                         ],
#                         'Projection': {
#                             'ProjectionType': 'ALL',
#                         },
#                         'ProvisionedThroughput': {
#                             'ReadCapacityUnits': 5, 
#                             'WriteCapacityUnits': 5,
#                         }
#                     }
#                 ]            
#         )

#     def clean_tables(self):
#         self.clean_table(self.chats_table_name)
#         self.clean_table(self.chats_logs_table_name)

#     def delete_tables(self):
#         self.delete_table(self.chats_logs_table_name)
#         self.delete_table(self.chats_table_name)


#     def get_table(self,table_name):
#         logger.info(f"get {table_name} table")
#         try:
#             table = self.dynamodb.Table(table_name)
#             logger.info(f"table {table_name} exists")
#             return table
#         except:
#             logger.info(f"table {table_name} was not created")

#     def clean_table(self,table_name):
#         logger.info(f"cleaning table '{table_name}'.")
#         try:
#             table = self.dynamodb.Table(table_name)
#             response = table.scan()
#             items = response.get('Items', [])

#             for item in items:
#                 table.delete_item(
#                     Key={key['AttributeName']: item[key['AttributeName']] for key in table.key_schema}
#                 )

#             logger.info(f"All records deleted from table '{table_name}'.")
#         except ClientError as e:
#             logger.error(f"Error cleaning table '{table_name}': {e.response['Error']['Message']}")

#     def create_table(self,table_name, key_schema, attribute_definitions,GlobalSecondaryIndexes=None):
#         logger.info(f"creating table '{table_name}'.")
#         try:
#             table_params = {
#                 'TableName': table_name,
#                 'KeySchema': key_schema,
#                 'AttributeDefinitions': attribute_definitions,
#                 'ProvisionedThroughput': {
#                     'ReadCapacityUnits': 5,
#                     'WriteCapacityUnits': 5
#                 }
#             }

#             if GlobalSecondaryIndexes is not None:
#                 table_params['GlobalSecondaryIndexes'] = GlobalSecondaryIndexes

#             table = self.dynamodb.create_table(**table_params)
#             table.wait_until_exists()
#             logger.info(f"Table '{table_name}' created successfully.")
#         except ClientError as e:
#             if e.response['Error']['Code'] == 'ResourceInUseException':
#                 logger.info(f"Table '{table_name}' already exists.")
#             else:
#                 logger.error(f"Error creating table '{table_name}': {e.response['Error']['Message']}")

#     def delete_table(self,table_name):
#         logger.info(f"delete table '{table_name}'.")
#         try:
#             table = self.dynamodb.Table(table_name)
#             table.delete()
#             logger.info(f"Table '{table_name}' deleted successfully.")
#         except NoCredentialsError as e:
#             logger.error(f"Error deleting table: {e}")
#         except Exception as e:
#             logger.error(f"Error deleting table: {e}")




#     def generate_chat_id(self):
#         return str(uuid.uuid4())

#     def get_current_date(self):
#         d = datetime.now()
#         date = str(d)
#         return date



#     def add_new_chat(self, title):
#         logger.info("dbmanager: add_new_chat")
#         chat_id = self.generate_chat_id()
#         date = self.get_current_date()
#         try:
#             res = DBManager.chats_table.put_item(Item={
#                 'chat_id': chat_id,
#                 'date': date,
#                 'title': title
#             })
#             logger.info("Chat table -Item added successfully!")
#             logger.debug(res)
#             return chat_id
#         except Exception as e:
#             logger.error(f"Error adding item: {e}")        

#     def get_chat_chat_logs(self,chat_id):
#         logger.info("dbmanager: get_chat_chat_logs")
#         try:
#             response = DBManager.chats_logs_table.query(
#                 IndexName='chat_id_index',
#                 KeyConditionExpression=Key('chat_id').eq(chat_id)
#             )
#             logs = sorted(response['Items'],key=lambda x: x['date'])
#             for d in logs:
#                 d.pop('chat_id', None)            
#             logger.info(f"got all chat logs successfuly")   
#             return logs
#         except Exception as e:
#             logger.error(f"Error getting chat log: {e}")   

#     def add_new_chat_log(self,chat_id, prompt,response):
#         logger.info("func:add_new_chat_log: adding new chat log")
#         prompt_id = self.generate_chat_id()
#         date = self.get_current_date()
#         try:
#             res = DBManager.chats_logs_table.put_item(Item={
#                 'prompt_id': prompt_id,
#                 'chat_id': chat_id,
#                 'date':date,
#                 'prompt': prompt,
#                 'response': response
                
#             })
#             logger.info("table chats logs item added successfully!")
#             logger.debug(res)
#             new_log =  {
#                 "prompt_id":prompt_id,
#                 "date":date,
#                 "prompt":prompt,
#                 "response":response
#             }
#             return new_log    
#         except Exception as e:
#             logger.error(f"Error adding item: {e}")        
#             return False

#     def get_all_chats(self):
#         logger.info("dbmanager:func:get_all_chats")
#         response = DBManager.chats_table.scan()
#         chats = response.get('Items', [])
#         chats.sort(key=lambda x: x['date'])
#         return chats

#     def get_all_chats_with_logs(self):
#         logger.info("dbmanager:func:get_all_chats_with_logs")
#         response = DBManager.chats_table.scan()
#         chats = response.get('Items', [])
#         chats.sort(key=lambda x: x['date'])
#         chat_ids = [item['chat_id'] for item in chats]
#         all_chats_with_logs = [self.get_chat_with_logs(chat_id) for chat_id in chat_ids]
#         return all_chats_with_logs

#     def get_chat_with_logs(self,chat_id):
#         logger.info(f"dbmanager:func:get_chat_with_logs")
#         res = DBManager.chats_table.get_item(Key={'chat_id': chat_id})
#         if 'Item' not in res:
#             return None        
#         chat_data = res['Item']
#         title = chat_data['title']
#         date = chat_data['date']
#         logs = self.get_chat_chat_logs(chat_id)
#         if not logs:
#             logs = []
#         chat_details = {
#             'chat_id': chat_id,
#             'title': title,
#             'date': date,
#             'logs': logs
#         }
#         return chat_details

#     def delete_chat(self,chat_id):
#         logger.info("dbmanager:func:delete_chat")
#         deletes_res = self.delete_chat_logs(chat_id)
#         if deletes_res:
#             response = self.chats_table.delete_item(
#                 Key={
#                     'chat_id': chat_id
#                 }
#             )
#             status_code = response['ResponseMetadata']['HTTPStatusCode']
#             if status_code == 200:
#                 return True
        
#     def delete_chat_logs(self,chat_id):
#         logger.info("dbmanager:func:delete_chat_logs")
#         response = self.chats_logs_table.scan(
#             FilterExpression='chat_id = :val',
#             ExpressionAttributeValues={
#                 ':val': {'S': chat_id}
#             }
#         )
#         for item in response.get('Items', []):
#             response_delete = self.chats_logs_table.delete_item(
#                 Key={
#                     'prompt_id': item['prompt_id']
#                 }
#             )
#             status_code = response['ResponseMetadata']['HTTPStatusCode']
#             if status_code != 200:
#                 return None
#         return True


# STAGE = os.getenv("STAGE", "Dev")
# NAMESPACE = os.getenv("POWERTOOLS_METRICS_NAMESPACE", "ServerlessConversation")
# CONF = get_aws_config()


# app = APIGatewayRestResolver()
# tracer = Tracer()
# logger = Logger(serialize_stacktrace=True,level=logging.DEBUG)
# metrics = Metrics(namespace="ServerlessConversation")

# s3 = boto3.client("s3",**CONF)    
# dynamodb = boto3.resource('dynamodb',**CONF)

# bucket_name = "test-bucket"
# model_manager = ModelManager(s3,bucket_name)
# db_manager = DBManager(dynamodb)

# cors = True



# # Lambdas 






# # Warm Up Lambda
# @logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
# @tracer.capture_lambda_handler
# @metrics.log_metrics(capture_cold_start_metric=True)
# def warm_up_handler(event, context):
#     db_manager.create_tables()
#     create_bucket(bucket_name)
#     response =  model_manager.upload_model()
#     res = {
#         'statusCode': 200,
#         'body': json.dumps(response)
#     }
#     return res  
  

# # Warm Down Lambda
# @logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
# @tracer.capture_lambda_handler
# @metrics.log_metrics(capture_cold_start_metric=True)
# def cool_down_handler(event, context):
#     clean_bucket(bucket_name)
#     delete_bucket(bucket_name)
#     db_manager.clean_tables()
#     db_manager.delete_tables()
#     return {
#         'statusCode': 200,
#     }


from deps import *

@app.get("/hello",cors=cors)
@tracer.capture_method
def hello() -> Response:
    # adding custom metrics
    # See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/metrics/
    metrics.add_metric(name="HelloWorldInvocations", unit=MetricUnit.Count, value=1)
    # structured log
    # See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/logger/
    logger.info("Hello world API ")
    return {"message": "hello world"}



@app.get("/c",cors=cors)
@tracer.capture_method
def chats() -> Response:
    metrics.add_metric(name="ChatsInvocations", unit=MetricUnit.Count, value=1)
    logger.info("Get All Chats API")
    chats_data = db_manager.get_all_chats()
    return {
        "statusCode":200,
        "data": chats_data}

@app.get("/cl",cors=cors)
@tracer.capture_method
def chats_with_logs() -> Response:
    metrics.add_metric(name="ChatsInvocations", unit=MetricUnit.Count, value=1)
    logger.info("Get All Chats with Logs API ")
    chats_data = db_manager.get_all_chats_with_logs()
    return {"data": chats_data}

@app.post("/c",cors=cors)
@tracer.capture_method
def new_chat() -> Response:
    metrics.add_metric(name="NewChatInvocations", unit=MetricUnit.Count, value=1)
    logger.info("Inside Method Post New Chat API")
    data = app.current_event.body
    json_data = json.loads(data)
    prompt = json_data["prompt"]
    if not prompt:
        return {
            "statusCode":400,
            "message":"prompt is missing"
        }        
    title = model_manager.predict_title(prompt)
    logger.info(title)
    chat_id = db_manager.add_new_chat(title)
    if chat_id:
        # chat_data = db_manager.get_chat_with_logs(chat_id)
        # if chat_data:
        #     return {
        #         "statusCode":200,
        #         "data":chat_data
        #     }    
        
        model_response = model_manager.predict_prompt(prompt)
        if model_response:
            res = db_manager.add_new_chat_log(chat_id,prompt,model_response)
            if res:
                chat_data = db_manager.get_chat_with_logs(chat_id)
                if chat_data:
                    return {
                        "statusCode":200,
                        "data":chat_data
                    }    
    return {
        "statusCode":500,
        "message":"Interval Error"
    }    

@app.delete("/c/<chat_id>",cors=cors)
@tracer.capture_method
def delete_chat(chat_id:str) -> Response:
    metrics.add_metric(name="DeleteChatsInvocations", unit=MetricUnit.Count, value=1)
    logger.info("Delete Chat API")
    res = db_manager.delete_chat(chat_id)
    if res:
        return {
            "statusCode":200
        }
    return {
        "statusCode":500,
        "message":"IntervalServerError"
    }

@app.get("/c/<chat_id>",cors=cors)
@tracer.capture_method
def chat(chat_id: str) -> Response:
    metrics.add_metric(name="ChatInvocations", unit=MetricUnit.Count, value=1)
    logger.info("Inside Method Get Chat API")
    chat_data = db_manager.get_chat_with_logs(chat_id)
    if chat_data:
        return {
            "statusCode":200,
            "data":chat_data
        }
    else:
        return {
            "statusCode":404,
            "message":"Doesnt not exists"
        } 
    
@app.put("/c/<chat_id>",cors=cors)
@tracer.capture_method
def converse(chat_id: str) -> Response:
    metrics.add_metric(name="ConverseInvocations", unit=MetricUnit.Count, value=1)
    logger.info("Inside Method Converse API")

    chat_data = db_manager.get_chat_with_logs(chat_id)
    if not chat_data:
        return {
            "statusCode":404,
            "message":"Doesnt not exists"
        }
    data = app.current_event.json_body
    prompt = data['prompt']
    if not prompt:
        return {
            "statusCode":400,
            "message":"prompt is missing"
        }        
    if not isinstance(prompt,str):
        return {
            "statusCode":400,
            "message":"prompt must be a string"
        }                
    history = [c['prompt'] for c in chat_data['logs']]
    history.append(prompt)
    model_response = model_manager.predict_prompt(history)
    if model_response:
        new_log = db_manager.add_new_chat_log(chat_id,prompt,model_response)
        if new_log:
            return {
                "statusCode":200,
                "data": new_log
            }  
    return {
        "statusCode":500,
        "message":"Interval Error"
    }  


# def get_warm_up_status():
#     logger.debug("func:get_warm_up_status: get status")
#     ongoing_status_indicator = "ongoing"
#     status = ongoing_status_indicator    
#     bucket = model_manager.s3_bucket
#     warm_up_key = model_manager.warm_up_key
#     try:
#         response = s3.get_object(Bucket=bucket, Key=warm_up_key)
#         status = response["Body"].read().decode("utf-8")
#     except s3.exceptions.NoSuchBucket:
#         status = ongoing_status_indicator
#     except s3.exceptions.NoSuchKey:
#         status = ongoing_status_indicator
#     return status


@lambda_handler_decorator
def lambda_middleware(handler, event, context) -> Callable:
    start_time = time.time()
    logger.info("Lambda Middleware....")
    if event['httpMethod'] == 'OPTIONS':
        logger.info("responding to preflight request....")
        response = {
            "statusCode": 200,
            "isBase64Encoded": 'false',
            "headers": {
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*",
            },
        }    
        return response
    
    logger.info("after preflight request....")
    status = get_warm_up_status()
    if status != model_manager.completed_status_indicator:
        logger.info("func:lambda_handler: status not completed... returning...")
        res = {
            'statusCode': 202,
            "body": json.dumps({"message":"The request has been accepted for processing, but the processing has not been completed"})
        }
        return res
    try:
        warm_up_status_execution_time = str(time.time() - start_time)
        start_time = time.time()
        db_manager.initilize_db()
        init_db_execution_time = str(time.time() - start_time)
        start_time = time.time()
        model_manager.initialize_model()
        init_model_execution_time = str(time.time() - start_time)
        
        execution_times = {
            "middleware_execution_times": {
                "warm_up_status":warm_up_status_execution_time,
                "init_db": init_db_execution_time,
                "init_model":init_model_execution_time
            }
        }
        exec_time_str = json.dumps(execution_times,indent=4)
        Logger.debug(exec_time_str)
    except Exception as e:
        logger.debug(f"Error in measuring execution times: {str(e)}")
        logger.error(f"Error in measuring execution times: {str(e)}")

    response = handler(event, context)
    # logger.info(response)
    body = response['body']
    status = response['statusCode']
    response = {
        "statusCode":status,
        "body":body,
        "headers": {
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
        },        
        "isBase64Encoded":'false',
    }
    response['body']
    # logger.info(response)
    return response



@lambda_middleware
@logger.inject_lambda_context(log_event=True,correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:  
    return app.resolve(event, context) 

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
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
    Response,
)
import json
from typing import Callable
import time
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
    # logger.info("Inside Method Post New Chat API")
    data = app.current_event.body
    json_data = json.loads(data)
    prompt = json_data["prompt"]
    if not prompt:
        return {
            "statusCode":400,
            "message":"prompt is missing"
        }        
    llm = ModelsManager.get_model()
    logger.debug(llm)
    title = llm.predict_title(prompt)
    logger.info(title)
    chat_id = db_manager.add_new_chat(title)
    if chat_id:
        # chat_data = db_manager.get_chat_with_logs(chat_id)
        # if chat_data:
        #     return {
        #         "statusCode":200,
        #         "data":chat_data
        #     }    
        
        model_response = llm.predict_prompt(prompt)
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
    llm = ModelsManager.get_model()
    model_response = llm.predict_prompt(history)
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

@app.get("/m",cors=cors)
def get_models() -> Response:
    available_options =[modelConf.to_json() for modelConf in  get_available_models()]
    
    return {
        "statusCode":200,
        "data": available_options
    }


@lambda_handler_decorator
def lambda_middleware(handler, event, context) -> Callable:
    start_time = time.time()
    # logger.info("Lambda Middleware....")
    if event['httpMethod'] == 'OPTIONS':
        # logger.info("responding to preflight request....")
        response = {
            "statusCode": 200,
            "isBase64Encoded": 'false',
            "headers": {
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*",
            },
            "body":json.dumps({"message":"preflight"})
        }    
        return response
    
    # ModelsManager.set_model(model_name="")
    # logger.info("after preflight request....")


    if event['httpMethod'] == 'POST' or event['httpMethod'] == 'PUT':
        data = json.loads(event['body'])
        model_name = data['model_name']
        model_conf = get_model(model_name)
        model_key = model_conf.model_key
        status = get_warm_up_status(model_key)
        logger.debug(status)
        completed_status_indicator = "completed"
        ongoing_status_indicator = "ongoing"
        fail_status_indicator = "failure"
        if status != completed_status_indicator:
            if status == ongoing_status_indicator: 
                logger.info("func:lambda_handler: status not completed... returning...")
                res = {
                    'statusCode': 202,
                    "body": json.dumps({"message":"The request has been accepted for processing, but the processing has not been completed"})
                }
                return res
            if status == fail_status_indicator:
                logger.info("func:lambda_handler: status  bas failed... returning...")
                res = {
                    'statusCode': 500,
                }
                return res  
        ModelsManager.set_model(model_name)

    try:
        warm_up_status_execution_time = str(time.time() - start_time)
        start_time = time.time()
        # model_manager.initialize_model()
        init_model_execution_time = str(time.time() - start_time)
        
        execution_times = {
            "middleware_execution_times": {
                "warm_up_status":warm_up_status_execution_time,
                "init_model":init_model_execution_time
            }
        }
        exec_time_str = json.dumps(execution_times,indent=4)
        # Logger.debug(exec_time_str)
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

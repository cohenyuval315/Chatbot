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

@app.get("/hello",cors=CORS)
@tracer.capture_method
def hello() -> Response:
    # adding custom metrics
    # See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/metrics/
    metrics.add_metric(name="HelloWorldInvocations", unit=MetricUnit.Count, value=1)
    # structured log
    # See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/logger/
    return make_lambda_message_response(200,"hello world")


@app.get("/c",cors=CORS)
@tracer.capture_method
def chats() -> Response:
    metrics.add_metric(name="ChatsInvocations", unit=MetricUnit.Count, value=1)
    chats_data = db_manager.get_all_chats()
    return make_lambda_data_response(chats_data)

@app.get("/cl",cors=CORS)
@tracer.capture_method
def chats_with_logs() -> Response:
    metrics.add_metric(name="ChatsInvocations", unit=MetricUnit.Count, value=1)
    chats_data = db_manager.get_all_chats_with_logs()
    return make_lambda_data_response(200,chats_data)



@app.post("/c",cors=CORS)
@tracer.capture_method
def new_chat() -> Response:
    metrics.add_metric(name="NewChatInvocations", unit=MetricUnit.Count, value=1)
    data = app.current_event.body
    json_data = json.loads(data)
    prompt = json_data["prompt"]        
    llm = ModelsManager.get_model()
    title = llm.predict_title(prompt)
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
                    return make_lambda_data_response(chat_data)
    return make_lambda_error_response(500)

@app.delete("/c/<chat_id>",cors=CORS)
@tracer.capture_method
def delete_chat(chat_id:str) -> Response:
    metrics.add_metric(name="DeleteChatsInvocations", unit=MetricUnit.Count, value=1)
    res = db_manager.delete_chat(chat_id)
    if res:
        return make_lambda_response(200)
    logger.error(f"failed to delete chat: error {res}")
    return make_lambda_error_response(500)

@app.get("/c/<chat_id>",cors=CORS)
@tracer.capture_method
def chat(chat_id: str) -> Response:
    metrics.add_metric(name="ChatInvocations", unit=MetricUnit.Count, value=1)
    chat_data = db_manager.get_chat_with_logs(chat_id)
    if chat_data:
        return make_lambda_data_response(chat_data)    
    return make_lambda_message_response(404,"Chat Does Not Exists")

    
@app.put("/c/<chat_id>",cors=CORS)
@tracer.capture_method
def converse(chat_id: str) -> Response:
    metrics.add_metric(name="ConverseInvocations", unit=MetricUnit.Count, value=1)
    chat_data = db_manager.get_chat_with_logs(chat_id)
    if not chat_data:
        return make_lambda_message_response(404,"Chat Does Not Exists")

    data = app.current_event.json_body
    prompt = data['prompt']
    history = [c['prompt'] for c in chat_data['logs']]
    history.append(prompt)
    llm = ModelsManager.get_model()
    model_response = llm.predict_prompt(history)

    if model_response:
        new_log = db_manager.add_new_chat_log(chat_id,prompt,model_response)
        if new_log:
            return make_lambda_data_response(new_log)
    return make_lambda_error_response(500)



@app.get("/m",cors=CORS)
def get_models() -> Response:
    available_options =[modelConf.to_user_json() for modelConf in  MODEL_AVAILABLE_OPTIONS]
    return make_lambda_data_response(available_options)



def get_status_response(status):
    if status == ONGOING_STATUS_INDICATOR: 
        logger.info("func:lambda_handler: status not completed... returning...")
        res = make_lambda_message_response(202,"The request has been accepted for processing, but the processing has not been completed")
        return res
    if status == FAIL_STATUS_INDICATOR:
        logger.info("func:lambda_handler: status  bas failed... returning...")
        res = make_lambda_error_response(500,"The request has been accepted for processing, but the processing has not been completed")
        return res 



@lambda_handler_decorator
def preflight_middleware(handler, event, context) -> Callable:
    if event['httpMethod'] == 'OPTIONS':
        res = make_lambda_message_response(200,"preflight")
        return res
    return handler(event, context)


@lambda_handler_decorator
def model_middleware(handler, event, context) -> Callable:
    if event['httpMethod'] == 'POST' or event['httpMethod'] == 'PUT': # methods that uses LLM model.
        data = json.loads(event['body'])
        model_name = data['model_name']
        model_conf = get_model(model_name)
        model_key = model_conf.model_key
        status = get_warm_up_status(model_key)
        if status != COMPLETED_STATUS_INDICATOR:
            res = get_status_response(status)
            return res 
        
        # model is available.
        ModelsManager.set_model(model_name)

    return handler(event, context)



@lambda_handler_decorator
def error_handler(handler, event, context) -> Callable:
    try:
        response = handler(event, context)
        return response
    except ServerlessException as se:
        filename , lineno, funcname, text = traceback.extract_tb(se.__trackback__)[-1]
        logger.error(f"filename: {filename} \nfunction: {funcname} \nline number: {lineno}, \ntext: {text} \nerror:{str(se)}")
        return make_lambda_error_response(500,"Interval Server Error")
    # except ClientException as ve:
    #     pass

    except TypeError as te:
        return make_lambda_error_response(400,f"Type Error")
    except KeyError as ke:
        return make_lambda_error_response(400,f"Missing Key")
    except Exception as e:
        filename , lineno, funcname, text = traceback.extract_tb(e.__trackback__)[-1]
        logger.error(f"filename: {filename} \nfunction: {funcname} \nline number: {lineno}, \ntext: {text} \nerror:{str(se)}")

@preflight_middleware
@model_middleware
@error_handler
@logger.inject_lambda_context(log_event=True,correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:  
    return app.resolve(event, context) 



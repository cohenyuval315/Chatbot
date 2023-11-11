from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit
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
)
import os 
import boto3
import transformers
import zipfile
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from transformers import T5Tokenizer, T5ForConditionalGeneration


# Globals
s3_bucket = "test-bucket"
model_name = "google/flan-t5-small"
model_key = "model_weights"
tokenizer_key = "model_tokenizer_weights"
warm_up_key = "warm_up_status.json"
completed_status_indicator = "completed"
ongoing_status_indicator = "ongoing"
fail_status_indicator = "failure"

class ModelManager:

    def __init__(self,s3):
        self.s3 = s3
        self.s3_bucket = "test-bucket"
        self.model_name = "google/flan-t5-small"
        self.model_key = "model_weights"
        self.tokenizer_key = "model_tokenizer_weights"
        self.model_local_path = "/tmp/model"
        self.tokenizer_local_path = "/tmp/tokenizer"
        self.model = None
        self.tokenizer = None
        self.is_initialized = False
        self._temp_s3_model_path = f"/tmp/model"
        self._temp_s3_tokenizer_path =  f"/tmp/tokenizer"

        self.warm_up_key = "warm_up_status.json"
        self.completed_status_indicator = "completed"
        self.ongoing_status_indicator = "ongoing"
        self.fail_status_indicator = "failure"

    def initialize_model(self):
        self.s3.download_file(self.s3_bucket, self.model_key, self.model_local_path)
        self.s3.download_file(self.s3_bucket, self.tokenizer_key, self.tokenizer_local_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_local_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_local_path)
        self.is_initialized = True

    def retrieve_model(self):
        if not self.is_initialized:
            self.initialize_model()
        return self.model, self.tokenizer
    
    def upload_model(self):
        try:
            self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=self.ongoing_status_indicator)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model.save_pretrained(self._temp_s3_model_path)
            tokenizer.save_pretrained(self._temp_s3_tokenizer_path)
            self.s3.upload_file(self._temp_s3_model_path, self.s3_bucket, self.model_key)
            self.s3.upload_file(self._temp_s3_tokenizer_path, self.s3_bucket, self.tokenizer_key)
            self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=self.completed_status_indicator)
        except:
            self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=self.fail_status_indicator)
            return {"status": self.fail_status_indicator}   
        return {"status": self.completed_status_indicator}

s3 = boto3.client("s3")    
model_manager = ModelManager(s3)
STAGE = os.getenv("STAGE", "dev")
NAMESPACE = os.getenv("POWERTOOLS_METRICS_NAMESPACE", "ServerlessConversation")
app = APIGatewayRestResolver()
tracer = Tracer()
logger = Logger(serialize_stacktrace=True)
metrics = Metrics(namespace="ServerlessConversation")
# metrics.set_default_dimensions(environment=STAGE, another="one")



# Warm Up Lambda
def warm_up_handler(event, context):
    return model_manager.upload_model()
    s3 = boto3.client("s3")
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    temp_model_path = f"/tmp/model"
    temp_tokenizer_path = f"/tmp/tokenizer"
    model.save_pretrained(temp_model_path)
    tokenizer.save_pretrained(temp_tokenizer_path)
    s3.upload_file(temp_model_path, s3_bucket, model_key)
    s3.upload_file(temp_tokenizer_path, s3_bucket, tokenizer_key)
    s3.put_object(Bucket=s3_bucket, Key=warm_up_key, Body=completed_status_indicator)

    return {"status": completed_status_indicator}



# Converse Lambda

def get_warm_up_status():
    # s3 = boto3.client("s3")
    ongoing_status_indicator = "ongoing"
    status = ongoing_status_indicator    
    try:
        response = s3.get_object(Bucket=s3_bucket, Key=warm_up_key)
        status = response["Body"].read().decode("utf-8")
    except s3.exceptions.NoSuchKey:
        status = ongoing_status_indicator
    return status

def predict(model,tokenizer,text_input,max_new_tokens=1000):
    inputs = tokenizer(text_input, return_tensors="pt")
    outputs = model.generate(**inputs,max_new_tokens=max_new_tokens)
    response = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    return response


@app.get(rule="/bad-request-error")
@tracer.capture_method
def bad_request_error():
    raise BadRequestError("Missing required parameter")  # HTTP  400

@app.get(rule="/not-found-error")
@tracer.capture_method
def not_found_error():
    raise NotFoundError  # HTTP 404


@app.get(rule="/internal-server-error")
@tracer.capture_method
def internal_server_error():
    raise InternalServerError("Internal server error")  # HTTP 500


@app.not_found
@tracer.capture_method
def handle_not_found_errors(exc: NotFoundError) -> Response:
    logger.info(f"Not found route: {app.current_event.path}")
    return Response(status_code=418, content_type=content_types.TEXT_PLAIN, body="I'm a teapot!")


@app.exception_handler(ValueError)
def handle_invalid_limit_qs(ex: ValueError):  # receives exception raised
    metadata = {"path": app.current_event.path, "query_strings": app.current_event.query_string_parameters}
    logger.error(f"Malformed request: {ex}", extra=metadata)

    return Response(
        status_code=400,
        content_type=content_types.TEXT_PLAIN,
        body="Invalid request parameters.",
    )

@app.get("/hello")
@tracer.capture_method
def hello() -> Response:
    # adding custom metrics
    # See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/metrics/
    metrics.add_metric(name="HelloWorldInvocations", unit=MetricUnit.Count, value=1)

    # structured log
    # See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/logger/
    logger.info("Hello world API - HTTP 200")
    return {"message": "hello world"}

@app.get("/c")
@tracer.capture_method
def chats() -> Response:
    metrics.add_metric(name="ChatsInvocations", unit=MetricUnit.Count, value=1)
    logger.info("Get All Chats API - HTTP 200")
    input_text = "A step by step recipe to make bolognese pasta:"
    model, tokenizer = model_manager.retrieve_model()
    output = predict(model,tokenizer,input_text)
    return {"message": "all chatss","output": f"{output}"}

@app.post("/c")
@tracer.capture_method
def new_chat() -> Response:
    metrics.add_metric(name="NewChatInvocations", unit=MetricUnit.Count, value=1)
    logger.info("New Chat API - HTTP 200")
    return {"message": "new_chat"}

@app.get("/c/<chat_id>")
@tracer.capture_method
def chat(chat_id: str) -> Response:
    metrics.add_metric(name="ChatInvocations", unit=MetricUnit.Count, value=1)
    logger.info("Get Chat API - HTTP 200")
    return {"message": "get_chat"}

@app.put("/c/<chat_id>")
@tracer.capture_method
def converse(chat_id: str) -> Response:
    metrics.add_metric(name="ConverseInvocations", unit=MetricUnit.Count, value=1)
    logger.info("Converse API - HTTP 200")
    return {"message": "converse"}




# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
# Adding tracer
# See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/tracer/
@tracer.capture_lambda_handler
# ensures metrics are flushed upon request completion/failure and capturing ColdStart metric
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:    
    status = get_warm_up_status()
    completed_status_indicator = "completed"
    logger.info("Model Upload Status: ", status)
    # if status != completed_status_indicator:
    #     logger.info("Stopping Lambda")
    #     return {"status": status}
    return app.resolve(event, context)

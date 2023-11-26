from aws_lambda_powertools.logging import correlation_paths
import json
from deps import *
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from typing import Callable
from botocore.exceptions import ClientError as BotoClientError


@lambda_handler_decorator
def error_handler(handler, event, context) -> Callable:
    try:
        response = handler(event, context)
        return response
    except ServerlessException as se:
        filename , lineno, funcname, text = traceback.extract_tb(se.__trackback__)[-1]
        logger.error(f"filename: {filename} \nfunction: {funcname} \nline number: {lineno}, \ntext: {text} \nerror:{str(se)}")
        return make_lambda_error_response(500,"Interval Server Error")
    # except TypeError as te:
    #     return make_lambda_error_response(400,f"Type Error")
    # except KeyError as ke:
    #     return make_lambda_error_response(400,f"Missing Key")
    # except Exception as e:
    #     pass
    # except s3.exceptions.NoSuchBucket:
    #     pass
    # except s3.exceptions.NoSuchKey:
    #     pass



def bucket_creations():
    try:
        if BUCKET_PER_MODEL is False:
            create_bucket(BUCKET_NAME)
        else:
            for b_name in get_models_buckets_names():
                create_bucket(b_name)
    except BotoClientError as botoerror:
        logger.warning(botoerror)


@error_handler
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    db_manager.create_tables()
    bucket_creations()
    ModelsManager.upload_all_models()
    return make_lambda_message_response(200,"warm up success!")


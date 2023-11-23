from aws_lambda_powertools.logging import correlation_paths
from deps import * 
import json

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    if BUCKET_PER_MODEL is False:
        clean_bucket(BUCKET_NAME)
        delete_bucket(BUCKET_NAME)
    else:
        for b_name in get_models_buckets_names():
                clean_bucket(b_name)
                delete_bucket(b_name)
    if DELETE_DYNAMO_DATA:
        db_manager.clean_tables()
    if DELETE_DYNAMO_TABLES:
        db_manager.delete_tables()
    res = {
        'statusCode': 200,
        'body': json.dumps({
            "message":"clean up success!"
        })
    }
    return res  


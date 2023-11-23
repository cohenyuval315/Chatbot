from aws_lambda_powertools.logging import correlation_paths
import json
from deps import *


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    db_manager.create_tables()
    create_bucket(BUCKET_NAME)
    response =  model_manager.upload_model()
    res = {
        'statusCode': 200,
        'body': json.dumps(response)
    }
    return res  
  

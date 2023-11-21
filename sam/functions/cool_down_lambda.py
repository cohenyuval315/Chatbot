from aws_lambda_powertools.logging import correlation_paths
from .deps import * 


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    clean_bucket(BUCKET_NAME)
    delete_bucket(BUCKET_NAME)
    db_manager.clean_tables()
    db_manager.delete_tables()
    return {
        'statusCode': 200,
    }



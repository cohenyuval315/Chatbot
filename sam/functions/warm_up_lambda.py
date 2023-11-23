from aws_lambda_powertools.logging import correlation_paths
import json
from deps import *
#logger,tracer,metrics,db_manager,create_bucket,BUCKET_NAME,model_manager


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    db_manager.create_tables()
    if BUCKET_PER_MODEL is False:
        create_bucket(BUCKET_NAME)
    else:
        for b_name in get_models_buckets_names():
            create_bucket(b_name)
            
    # response =  model_manager.upload_model()
    ModelsManager.upload_all_models()
    res = {
        'statusCode': 200,
        'body': json.dumps({
            "message":"warm up success!"
        })
    }
    return res  
  

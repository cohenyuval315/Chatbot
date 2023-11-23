# DOCKER_HOST=unix:///var/run/docker.sock
# docker localstack Network : Name: ipv4_address: 10.0.2.20 -> in application set dns to 10.0.2.20 and network to name . network name, ipam config, subnet 10.0.2.0/24

# LOCALSTACK_HOST=localhost.localstack.cloud:4566 \ 
# GATEWAY_LISTEN="0.0.0.0" \ 
# DOCKER_BRIDGE_IP="172.17.0.1" \ 
# default 10

#LAMBDA_DOCKER_FLAGS='-p 19891:19891' MAIN_DOCKER_NETWORK=$DOCKER_NETWORK DOCKER_FLAGS="--network $DOCKER_NETWORK" LAMBDA_RUNTIME_ENVIRONMENT_TIMEOUT=60 LAMBDA_DOCKER_NETWORK=$DOCKER_NETWORK IAM_SOFT_MODE=1 ENFORCE_IAM=1 
# DISABLE_CUSTOM_CORS_APIGATEWAY=1 DISABLE_CORS_CHECKS=1 DISABLE_CORS_HEADERS=1 DEBUG=1 localstack start -d

# application
# ARGS=
# IMAGE=
# docker run --rm -it --dns $ADDRESS --network $DOCKER_NETWORK $ARGS $IMAGE



#local HTTP server that simulates API Gateway (2).: 
#aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws



# samlocal list endpoints --stack-name chatbot --output json
# samlocal logs --stack-name chatbot
# samlocal remote invoke LambdaFunction --stack-name chatbot


# DEBUGGER
# samlocal local start-api --warm-containers eager --debug -p 3001
# DEBUGGER_ARGS="-m ikpdb --ikpdb-port=5858 --ikpdb-working-directory=/var/task/ --ikpdb-client-working-directory=/myApp --ikpdb-address=0.0.0.0" echo {} | sam local invoke -d 5858 myFunction


#--container-host-interface 0.0.0.0 --container-host host.docker.internal
# samlocal local start-api --warm-containers eager --debug -p 3001

#python3 -m pytest ../tests/unit



# build event
# sam local generate-event --help
# sam local generate-event [SERVICE] --help
# #Generates the event from S3 when a new object is created
# sam local generate-event s3 put


# # Generates the event from S3 when an object is deleted
# sam local generate-event s3 delete

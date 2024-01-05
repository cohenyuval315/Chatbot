
echo 'initlizing localstack...'
echo 'stoping existing localstack instances...'
localstack stop >/dev/null 2>&1


echo 'create localstack network if not exists...'
DOCKER_NETWORK=localstack-network
docker network inspect $DOCKER_NETWORK >/dev/null 2>&1 || \ 
docker network create --driver bridge $DOCKER_NETWORK




# DOCKER_HOST=unix:///var/run/docker.sock
# docker localstack Network : Name: ipv4_address: 10.0.2.20 -> in application set dns to 10.0.2.20 and network to name . network name, ipam config, subnet 10.0.2.0/24

# LOCALSTACK_HOST=localhost.localstack.cloud:4566 \ 
# GATEWAY_LISTEN="0.0.0.0" \ 
# DOCKER_BRIDGE_IP="172.17.0.1" \ 
# default 10

#LAMBDA_DOCKER_FLAGS='-p 19891:19891' MAIN_DOCKER_NETWORK=$DOCKER_NETWORK DOCKER_FLAGS="--network $DOCKER_NETWORK" LAMBDA_RUNTIME_ENVIRONMENT_TIMEOUT=60 LAMBDA_DOCKER_NETWORK=$DOCKER_NETWORK IAM_SOFT_MODE=1 ENFORCE_IAM=1 
DISABLE_CUSTOM_CORS_APIGATEWAY=1 DISABLE_CORS_CHECKS=1 DISABLE_CORS_HEADERS=1 DEBUG=1 localstack start # -d


ADDRESS=$(docker inspect localstack_main | jq -r '.[0].NetworkSettings.Networks | to_entries | .[].value.IPAddress')
echo "$ADDRESS"

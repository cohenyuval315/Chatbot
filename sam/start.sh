

PORT=3001
ADDRESS=$(docker inspect localstack-main | jq -r '.[0].NetworkSettings.Networks | to_entries | .[].value.IPAddress')
echo "please verify that this address equals functions.deps.config.endpoint_url = $ADDRESS ..."


sam local start-api --warm-containers eager --docker-network bridge  -p $PORT

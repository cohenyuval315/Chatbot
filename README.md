An Interactive Serverless chat bot react web application based on huggingface LLM models, built with localstack aws features which includes apigateway , lambdas , s3 , dynamodb and AWS SAM.


- make sure docker service is running

recommds using unix , cloud formation very slow on wsl2
## start serverless (unix/wsl2):
```code
cd ./sam/scripts/
dos2unix start_localstack.sh
./start_localstack.sh
./build
./start
```

## start react:
```code
cd web
npm install
npm start
```

## configuration files:
- /sam/functions/deps/config.py - configuration of the lambdas functions.
- /sam/functions/deps/globals.py -  
- /sam/templates.yaml - AWS SAM template which built on cloudformation. 

## lambda functions:
- WarmUpFunction (warm_up_function.py) - initialize dynamodb, get all the models requested, compress them, and upload them to s3.
- ConverseFunction (lambda_function.py) - using lambda powertools ,describes all the available chat bot services.
- CoolDownFunction (cool_down_function.py) - delete/clean database, s3 

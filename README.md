An Interactive Serverless chat bot react web application using on huggingface LLM models, built with localstack aws features which includes apigateway , lambdas , s3 , dynamodb and AWS SAM.

the models used are relativily small sized for performance, so the answers are not very corehent 
its always possible to add more models/other models depending on ur hardware constrants :)


```code
- make sure docker service is running
- docker compose up -d
- dos2unix for sh files if needed.
- cd ./sam 
- ./build.sh - (in wsl2 will take extremly long time unforturtantly. so use unix if you can)
- ./start.sh  - it will print ip address of localstack on console please use localstack ip address in endpoint_url in config file functions/deps/config. 


## start serverless (unix/wsl2):
```

## configuration files:
- /sam/functions/deps/config.py - configuration of the lambdas functions.
- /sam/templates.yaml - AWS SAM template which built on cloudformation. 
- /sam/functions/deps/models.py- here you can see all the models used, you can add anything, as long as the name corespond to the model name avaialble in hugging face.

## lambda functions:
- WarmUpFunction (warm_up_function.py) - initialize dynamodb, buckets in s3, get all the models requested, compress them, and upload them to s3.
- ConverseFunction (lambda_function.py) - using lambda powertools ,describes all the available chat bot services.
- CoolDownFunction (cool_down_function.py) - delete/clean database, s3 


## images
## start screen 

![Start Screen](/Chatbot/docs/start_screen.png)
![Chat Screen](/Chatbot/docs/chat_screen.png)
![Chat Loading Screen](/Chatbot/docs/chat_loading_screen.png)
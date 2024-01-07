# Project Overview

## Interactive Serverless Chat Bot Application
This project introduces an Interactive Serverless Chat Bot web application powered by LLM models from Hugging Face, designed to engage users through dynamic conversations.

<strong>READ ME: </strong> Scroll down to discover how to start the chatbot, and view the architecture images, application snapshots and videos showcasing the chatbot.

## Project Stack
- React Web
- Python-based Lambdas using Lambda Power Tools
- Hugging Face Transformers
- AWS LocalStack featuring Lambda, API Gateway REST, S3, SAM/CloudFormation, DynamoDB

## Development Timeline

- **Total Hours Invested:** Around 150 hours
- **Development Duration:** 2 weeks
- **Refinement and Adjustments:** 1 week


## Project Objective
The fundamental drive behind this project was to seamlessly integrate various AWS services, prioritizing hands-on experience to bolster proficiency in AWS basics. The deliberate exploration sought to lay a robust foundation for navigating and utilizing a spectrum of AWS services effectively.
The specific drive for this project came from a wish to create my own chatbot. What I wanted was straightforward: an easy way to change and test chatbot models. So, the project's aim was to set up a chatbot where I could effortlessly add or switch models, all within a user-friendly interface.


## Learning AWS Basics

The project's core focus on AWS integration enabled a hands-on learning experience, providing insights into essential AWS services such as API Gateway, Lambdas, S3, DynamoDB, and AWS SAM. This practical exposure has significantly contributed to gaining proficiency in AWS basics. although not used this helped me gained understand about many features that are not used, such as identity management(iam) roles and policies, and lambda layers
Inspired by SageMaker capabilities showcased at an AWS conference, I chose to incorporate it into the project to deepen my understanding of AWS features. Given that LocalStack SageMaker is a pro feature, a custom implementation was pursued. Leveraging Hugging Face, which integrates with AWS SageMaker, proved to be a strategic decision due to its open-source nature and support from SageMaker.

## Noteworthy Achievements
- Advancement in proficiency with common AWS services.
- Successful implementation of an Interactive Serverless Chat Bot using React and Hugging Face LLM models.
- Utilization of LocalStack AWS features for seamless integration of AWS services.
- Purposeful use of small-sized models for optimal performance, with the flexibility to incorporate additional models based on hardware constraints.
- Seamless interaction within the React web browser.
- Enhanced proficiency in Docker's networking.

## Challenges and Insights

- Integration of SAM (CloudFormation) with LocalStack posed significant challenges.
- WSL2 compatibility issues were encountered.
- SAM local testing required manual IP configuration for using LocalStack, and similar challenges were faced during SAM deploy (not compatible with LocalStack, necessitating manual/scripted deployment of Lambdas).
- Serverless applications typically involve significantly less boilerplate code compared to traditional server-based applications. This reduction in boilerplate code not only facilitates easier development but also contributes to cost savings, particularly in the context of new products. (It's essential to note, however, that the cost-effectiveness of serverless may be less pronounced when the application requires significant scaling to handle a large number of requests.)
- 

## Acknowledgments
- AWS Free Cloud Practitioner Course: Completed more than half of the course, paused to implement newly acquired knowledge, and adhered to responsibilities. This experience significantly deepened my understanding.
- Boto3 Documentation
- AWS Documentation
- LocalStack Documentation
- Stack Overflow
- Docker Documentation
- Hugging Face Transformers Documentation
---

# architechture
<h2 align="center">admin flow</h2>

![admin_chat_bot_flow](https://github.com/cohenyuval315/Chatbot/assets/61754002/a03d7d2a-1420-4172-8da5-26c206367376)

<h2 align="center">user flow</h2>

![user_chat_bot_flow](https://github.com/cohenyuval315/Chatbot/assets/61754002/4fb01466-2105-4a63-a23a-ac8d7539ae5e)


## How to Start

1. Ensure Docker service is running.
2. Run `docker compose up -d`.
3. If needed, execute `dos2unix` on shell files.
4. Navigate to the `./sam` directory.
5. Execute `./build.sh` (Note: On WSL2, this may take an extended time; consider using Unix).
6. Run `./start.sh` and note the localstack IP address displayed in the console. Use this IP address as `endpoint_url` in the configuration file `functions/deps/config`.
7. run lambda warm up function, to initialize the db and fetch the models from hungging face. (localhost:3001/start)
8. open web browser at localhost:3000.
9. happy chating :)

## Configuration Files
- `/sam/functions/deps/config.py`: Configuration for Lambda functions.
- `/sam/templates.yaml`: AWS SAM template built on CloudFormation.
- `/sam/functions/deps/models.py`: Lists and define all models used; add more models ensuring names correspond to those available in Hugging Face.

## Lambda Functions

1. **WarmUpFunction (warm_up_function.py):**
   - Initializes DynamoDB, S3 buckets, retrieves requested models, compresses, and uploads them to S3.

2. **ConverseFunction (lambda_function.py):**
   - Utilizes Lambda Powertools to describe all available chat bot services.

3. **CoolDownFunction (cool_down_function.py):**
   - Deletes/cleans the database and S3 storage.


# Application Screenshots and videos
## Images
- **Start Screen:**
![start_screen](https://github.com/cohenyuval315/Chatbot/assets/61754002/ce90ce60-fc50-44e3-ba1f-a242104116a2)

- **Chat Screen:**
![chat_screen](https://github.com/cohenyuval315/Chatbot/assets/61754002/4aac2072-2723-47a0-83a8-a64a75fb742c)

- **Chat Loading Screen:**
![chat_loading_screen](https://github.com/cohenyuval315/Chatbot/assets/61754002/f4034305-17c4-425a-a480-433013f05e2c)

## Videos
The videos may exhibit some lag, but it's important to note that the lag is only present in the recordings. In actual usage, the chatbot operates seamlessly. The computer used for recording and chatbot interactions has limited resources
  
[fastmodel.webm](https://github.com/cohenyuval315/Chatbot/assets/61754002/e27ff9d5-5459-4a20-a3c6-f0ed5de85fe9)

In this video, both Flan T5 small and base models are utilized. It serves to highlight the performance differences between the two models, providing insights into the impact of model size on chatbot responsiveness.

[bothmodels.webm](https://github.com/cohenyuval315/Chatbot/assets/61754002/230ebc83-7f99-419c-ad2c-6da1ec8ce38d)


from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError,NoCredentialsError
import uuid
from datetime import datetime
from .logger import logger


class DBManager:
    chats_table = None
    chats_logs_table = None

    def __init__(self,dynamodb) -> None:
        self.dynamodb = dynamodb
        self.chats_table_name = 'chats'
        self.chats_logs_table_name = 'chats_logs'

    def initilize_db(self):
        DBManager.chats_table = self.get_table(self.chats_table_name)
        DBManager.chats_logs_table = self.get_table(self.chats_logs_table_name)

    def create_tables(self):
        logger.info("creating tables")
        self.create_table(
            table_name=self.chats_table_name,
            key_schema=[
                {'AttributeName': 'chat_id', 'KeyType': 'HASH'},
            ],
            attribute_definitions=[
                {'AttributeName': 'chat_id', 'AttributeType': 'S'},
            ]
        )
        self.create_table(
            table_name=self.chats_logs_table_name,
            key_schema=[
                {'AttributeName': 'prompt_id', 'KeyType': 'HASH'},
            ],
            attribute_definitions=[
                {'AttributeName': 'prompt_id', 'AttributeType': 'S'},
                {'AttributeName': 'chat_id', 'AttributeType': 'S'},
            ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'chat_id_index',
                        'KeySchema': [
                            {'AttributeName': 'chat_id', 'KeyType': 'HASH'},
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL',
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5, 
                            'WriteCapacityUnits': 5,
                        }
                    }
                ]            
        )

    def clean_tables(self):
        self.clean_table(self.chats_table_name)
        self.clean_table(self.chats_logs_table_name)

    def delete_tables(self):
        self.delete_table(self.chats_logs_table_name)
        self.delete_table(self.chats_table_name)


    def get_table(self,table_name):
        logger.info(f"get {table_name} table")
        try:
            table = self.dynamodb.Table(table_name)
            logger.info(f"table {table_name} exists")
            return table
        except:
            logger.info(f"table {table_name} was not created")

    def clean_table(self,table_name):
        logger.info(f"cleaning table '{table_name}'.")
        try:
            table = self.dynamodb.Table(table_name)
            response = table.scan()
            items = response.get('Items', [])

            for item in items:
                table.delete_item(
                    Key={key['AttributeName']: item[key['AttributeName']] for key in table.key_schema}
                )

            logger.info(f"All records deleted from table '{table_name}'.")
        except ClientError as e:
            logger.error(f"Error cleaning table '{table_name}': {e.response['Error']['Message']}")

    def create_table(self,table_name, key_schema, attribute_definitions,GlobalSecondaryIndexes=None):
        logger.info(f"creating table '{table_name}'.")
        try:
            table_params = {
                'TableName': table_name,
                'KeySchema': key_schema,
                'AttributeDefinitions': attribute_definitions,
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }

            if GlobalSecondaryIndexes is not None:
                table_params['GlobalSecondaryIndexes'] = GlobalSecondaryIndexes

            table = self.dynamodb.create_table(**table_params)
            table.wait_until_exists()
            logger.info(f"Table '{table_name}' created successfully.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"Table '{table_name}' already exists.")
            else:
                logger.error(f"Error creating table '{table_name}': {e.response['Error']['Message']}")

    def delete_table(self,table_name):
        logger.info(f"delete table '{table_name}'.")
        try:
            table = self.dynamodb.Table(table_name)
            table.delete()
            logger.info(f"Table '{table_name}' deleted successfully.")
        except NoCredentialsError as e:
            logger.error(f"Error deleting table: {e}")
        except Exception as e:
            logger.error(f"Error deleting table: {e}")




    def generate_chat_id(self):
        return str(uuid.uuid4())

    def get_current_date(self):
        d = datetime.now()
        date = str(d)
        return date



    def add_new_chat(self, title):
        logger.info("dbmanager: add_new_chat")
        chat_id = self.generate_chat_id()
        date = self.get_current_date()
        try:
            res = DBManager.chats_table.put_item(Item={
                'chat_id': chat_id,
                'date': date,
                'title': title
            })
            logger.info("Chat table -Item added successfully!")
            logger.debug(res)
            return chat_id
        except Exception as e:
            logger.error(f"Error adding item: {e}")        

    def get_chat_chat_logs(self,chat_id):
        logger.info("dbmanager: get_chat_chat_logs")
        try:
            response = DBManager.chats_logs_table.query(
                IndexName='chat_id_index',
                KeyConditionExpression=Key('chat_id').eq(chat_id)
            )
            logs = sorted(response['Items'],key=lambda x: x['date'])
            for d in logs:
                d.pop('chat_id', None)            
            logger.info(f"got all chat logs successfuly")   
            return logs
        except Exception as e:
            logger.error(f"Error getting chat log: {e}")   

    def add_new_chat_log(self,chat_id, prompt,response):
        logger.info("func:add_new_chat_log: adding new chat log")
        prompt_id = self.generate_chat_id()
        date = self.get_current_date()
        try:
            res = DBManager.chats_logs_table.put_item(Item={
                'prompt_id': prompt_id,
                'chat_id': chat_id,
                'date':date,
                'prompt': prompt,
                'response': response
                
            })
            logger.info("table chats logs item added successfully!")
            logger.debug(res)
            new_log =  {
                "prompt_id":prompt_id,
                "date":date,
                "prompt":prompt,
                "response":response
            }
            return new_log    
        except Exception as e:
            logger.error(f"Error adding item: {e}")        
            return False

    def get_all_chats(self):
        logger.info("dbmanager:func:get_all_chats")
        response = DBManager.chats_table.scan()
        chats = response.get('Items', [])
        chats.sort(key=lambda x: x['date'])
        return chats

    def get_all_chats_with_logs(self):
        logger.info("dbmanager:func:get_all_chats_with_logs")
        response = DBManager.chats_table.scan()
        chats = response.get('Items', [])
        chats.sort(key=lambda x: x['date'])
        chat_ids = [item['chat_id'] for item in chats]
        all_chats_with_logs = [self.get_chat_with_logs(chat_id) for chat_id in chat_ids]
        return all_chats_with_logs

    def get_chat_with_logs(self,chat_id):
        logger.info(f"dbmanager:func:get_chat_with_logs")
        res = DBManager.chats_table.get_item(Key={'chat_id': chat_id})
        if 'Item' not in res:
            return None        
        chat_data = res['Item']
        title = chat_data['title']
        date = chat_data['date']
        logs = self.get_chat_chat_logs(chat_id)
        if not logs:
            logs = []
        chat_details = {
            'chat_id': chat_id,
            'title': title,
            'date': date,
            'logs': logs
        }
        return chat_details

    def delete_chat(self,chat_id):
        logger.info("dbmanager:func:delete_chat")
        deletes_res = self.delete_chat_logs(chat_id)
        if deletes_res:
            response = self.chats_table.delete_item(
                Key={
                    'chat_id': chat_id
                }
            )
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            if status_code == 200:
                return True
        
    def delete_chat_logs(self,chat_id):
        logger.info("dbmanager:func:delete_chat_logs")
        response = self.chats_logs_table.scan(
            FilterExpression='chat_id = :val',
            ExpressionAttributeValues={
                ':val': {'S': chat_id}
            }
        )
        for item in response.get('Items', []):
            response_delete = self.chats_logs_table.delete_item(
                Key={
                    'prompt_id': item['prompt_id']
                }
            )
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            if status_code != 200:
                return None
        return True

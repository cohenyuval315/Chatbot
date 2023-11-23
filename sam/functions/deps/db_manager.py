from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError,NoCredentialsError
import uuid
from datetime import datetime
from .logger import logger
from .singleton_base import SingletonBase

def generate_chat_id():
    return str(uuid.uuid4())

def get_current_date():
    d = datetime.now()
    date = str(d)
    return date


class DynamoTable(SingletonBase):

    def __init__(self,dynamodb_instance,table_name:str,table_configuration:dict) -> None:
        super().__init__(table_name)        
        self.dynamodb = dynamodb_instance
        self.table_name = table_name
        self.table_configuration = table_configuration
        self._key_schema_key = "KeySchema"
        self._attribute_definitions_key = "AttributeDefinitions"
        self._global_secondary_key = "GlobalSecondaryIndexes"

        self._validate_configuration(self.table_configuration)
        self.key_schema = self.table_configuration[f"{self._key_schema_key}"]
        self.attribute_definitions = self.table_configuration[f"{self._attribute_definitions_key}"]
        self.table_params = {
            'TableName': self.table_name,
            'KeySchema': self.key_schema,
            'AttributeDefinitions': self.attribute_definitions,
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
        if self._global_secondary_key in self.table_configuration.keys():
            self.table_params[f"{self._global_secondary_key}"] = table_configuration[f"{self._global_secondary_key}"]

    def _validate_configuration(self,table_configuration:dict):
        keys = table_configuration.keys()
        if self._key_schema_key not in keys:
            raise ValueError(f"missing key in table configuration {self._key_schema_key}")
        else:
            if not isinstance(table_configuration[f"{self._key_schema_key}"],list):
                raise ValueError(f"invalid key type in table configuration {self._key_schema_key} : should be a list . type:  {type(table_configuration[f'{self._key_schema_key}'])}")
            else:
                for item in table_configuration[f"{self._key_schema_key}"]:
                    if not isinstance(item,dict):
                        raise ValueError(f"invalid item type in {self._key_schema_key} . should be a json . type:  {type(item)}")
                    
        if self._attribute_definitions_key not in keys:
            raise ValueError(f"missing key in table configuration {self._attribute_definitions_key}")
        else:
            if not isinstance(table_configuration[f"{self._attribute_definitions_key}"],list):
                raise ValueError(f"invalid key type in table configuration {self._attribute_definitions_key} : should be a list . type:  {type(table_configuration[f'{self._attribute_definitions_key}'])}")
            else:
                for item in table_configuration[f"{self._attribute_definitions_key}"]:
                    if not isinstance(item,dict):
                        raise ValueError(f"invalid item type in {self._attribute_definitions_key} . should be a json . type:  {type(item)}")

        if self._global_secondary_key in keys:
            if not isinstance(table_configuration[f"{self._global_secondary_key}"],list):
                raise ValueError(f"invalid key type in table configuration {self._global_secondary_key} : should be a list . type:  {type(table_configuration[f'{self._global_secondary_key}'])}")
            else:
                for item in table_configuration[f"{self._global_secondary_key}"]:
                    if not isinstance(item,dict):
                        raise ValueError(f"invalid item type in {self._global_secondary_key} . should be a json . type:  {type(item)}")

    def create_table(self):
        logger.info(f"creating table '{self.table_name}'.")
        try:
            table = self.dynamodb.create_table(**self.table_params)
            table.wait_until_exists()
            logger.info(f"Table '{self.table_name}' created successfully.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"Table '{self.table_name}' already exists.")
            else:
                logger.error(f"Error creating table '{self.table_name}': {e.response['Error']['Message']}")
            return False

    def get_table(self,create_if_not_exists=False):
        logger.info(f"get {self.table_name} table")
        try:
            table = self.dynamodb.Table(self.table_name)
            logger.info(f"table {self.table_name} exists")
            return table
        except:
            logger.info(f"table {self.table_name} was not created")
            if create_if_not_exists:
                create_res = self.create_table()
                if create_res is False:
                    raise Exception("Shouldnt Get Here")                
                return self.create_table(False)
            return False

    def clean_table(self):
        logger.info(f"cleaning table '{self.table_name}'.")
        try:
            table = self.dynamodb.Table(self.table_name)
            response = table.scan()
            items = response.get('Items', [])

            for item in items:
                table.delete_item(
                    Key={key['AttributeName']: item[key['AttributeName']] for key in table.key_schema}
                )

            logger.info(f"All records deleted from table '{self.table_name}'.")
        except ClientError as e:
            logger.error(f"Error cleaning table '{self.table_name}': {e.response['Error']['Message']}")

    def delete_table(self):
        logger.info(f"delete table '{self.table_name}'.")
        try:
            table = self.dynamodb.Table(self.table_name)
            table.delete()
            logger.info(f"Table '{self.table_name}' deleted successfully.")
        except NoCredentialsError as e:
            logger.error(f"Error deleting table: {e}")
        except Exception as e:
            logger.error(f"Error deleting table: {e}")

class Chats(DynamoTable):
    def __init__(self, dynamodb_instance) -> None:
        name = "chats"
        table_configuration = {
            "KeySchema":[
                {'AttributeName': 'chat_id', 'KeyType': 'HASH'},
            ],
            "AttributeDefinitions":[
                {'AttributeName': 'chat_id', 'AttributeType': 'S'},
            ]
        }
        super().__init__(dynamodb_instance, name, table_configuration)

class ChatsLogs(DynamoTable):
    def __init__(self, dynamodb_instance) -> None:
        name = "chats_logs"
        table_configuration = {
            "KeySchema":[
                {'AttributeName': 'prompt_id', 'KeyType': 'HASH'},
            ],
            "AttributeDefinitions":[
                {'AttributeName': 'prompt_id', 'AttributeType': 'S'},
                {'AttributeName': 'chat_id', 'AttributeType': 'S'},
            ],
            "GlobalSecondaryIndexes":[
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

        }
        super().__init__(dynamodb_instance, name, table_configuration)


class DynamoDB(SingletonBase):
    def __init__(self,dynamodb_instance):
        name = "DynamoDB"
        create_if_not_exists = True
        self.chats = Chats(dynamodb_instance)
        self.chats_logs = ChatsLogs(dynamodb_instance)
        self.chats_table = self.chats.get_table(create_if_not_exists)
        self.chats_logs_table = self.chats_logs.get_table(create_if_not_exists)
        super().__init__(name)

    def create_tables(self):
        self.chats.create_table()
        self.chats_logs.create_table()

    def clean_tables(self):
        self.chats_logs.clean_table()
        self.chats.clean_table()

    def delete_tables(self):
        self.chats_logs.delete_table()
        self.chats.delete_table()



    def add_new_chat(self, title):
        logger.info("dbmanager: add_new_chat")
        chat_id = generate_chat_id()
        date = get_current_date()
        try:
            res = self.chats_table.put_item(Item={
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
            response = self.chats_logs_table.query(
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
        prompt_id = generate_chat_id()
        date = get_current_date()
        try:
            res = self.chats_logs_table.put_item(Item={
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
        response = self.chats_table.scan()
        chats = response.get('Items', [])
        chats.sort(key=lambda x: x['date'])
        return chats

    def get_all_chats_with_logs(self):
        logger.info("dbmanager:func:get_all_chats_with_logs")
        response = self.chats_table.scan()
        chats = response.get('Items', [])
        chats.sort(key=lambda x: x['date'])
        chat_ids = [item['chat_id'] for item in chats]
        all_chats_with_logs = [self.get_chat_with_logs(chat_id) for chat_id in chat_ids]
        return all_chats_with_logs

    def get_chat_with_logs(self,chat_id):
        logger.info(f"dbmanager:func:get_chat_with_logs")
        res = self.chats_table.get_item(Key={'chat_id': chat_id})
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



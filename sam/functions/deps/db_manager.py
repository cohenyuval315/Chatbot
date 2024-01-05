from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError,NoCredentialsError
import uuid
from datetime import datetime
from .logger import logger
from .singleton_base import SingletonBase

def generate_chat_id() -> str:
    return str(uuid.uuid4())

def get_current_date() -> str:
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

        self.table = self.get_table()

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
        try:
            table = self.dynamodb.create_table(**self.table_params)
            table.wait_until_exists()        
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                pass
            else:
                raise e

    def get_table(self,create_if_not_exists:bool=True):
        try:
            table = self.dynamodb.Table(self.table_name)
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                if create_if_not_exists:
                    self.create_table()
                    return self.get_table(False)
            raise e from e
            
    def clean_table(self):
        table = self.dynamodb.Table(self.table_name)
        response = table.scan()
        items = response.get('Items', [])

        for item in items:
            table.delete_item(
                Key={key['AttributeName']: item[key['AttributeName']] for key in table.key_schema}
            )

    def delete_table(self):
        table = self.dynamodb.Table(self.table_name)
        table.delete()
        logger.info(f"Table '{self.table_name}' deleted successfully.")


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
        
    def get_all_chats(self):
        response = self.table.scan()
        chats = response.get('Items', [])
        chats.sort(key=lambda x: x['date'])
        return chats

    def create_chat(self, title:str):
        chat_id = generate_chat_id()
        date = get_current_date()        
        self.table.put_item(Item={
            'chat_id': chat_id,
            'date': date,
            'title': title
        })
        return chat_id

    def delete_chat(self,chat_id:str):
        response = self.table.delete_item(
            Key={
                'chat_id': chat_id
            }
        )
        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code == 200:
            return True

    def get_chat(self,chat_id:str):
        res = self.table.get_item(Key={'chat_id': chat_id})
        if 'Item' not in res:
            return None        
        chat_data = res['Item']
        title = chat_data['title']
        date = chat_data['date']
        chat_details = {
            'chat_id': chat_id,
            'title': title,
            'date': date,
        }
        return chat_details



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

    def create_chat_log(self,chat_id:str, prompt:str,response:str):
        prompt_id = generate_chat_id()
        date = get_current_date()
        self.table.put_item(Item={
            'prompt_id': prompt_id,
            'chat_id': chat_id,
            'date':date,
            'prompt': prompt,
            'response': response,
        })

        new_log =  {
            "prompt_id":prompt_id,
            "date":date,
            "prompt":prompt,
            "response":response
        }
        return new_log      
    
    def get_chat_logs(self,chat_id:str):
        response = self.table.query(
            IndexName='chat_id_index',
            KeyConditionExpression=Key('chat_id').eq(chat_id)
        )
        logs = sorted(response['Items'],key=lambda x: x['date'])
        for d in logs:
            d.pop('chat_id', None)            
        return logs
    
    def delete_chat_logs(self,chat_id:str):
        response = self.table.scan(
            FilterExpression='chat_id = :val',
            ExpressionAttributeValues={
                ':val': {'S': chat_id}
            }
        )
        for item in response.get('Items', []):
            self.table.delete_item(
                Key={
                    'prompt_id': item['prompt_id']
                }
            )
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            if status_code != 200:
                return None
        return True


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

    def add_new_chat(self, title:str):
        return self.chats.create_chat(title)

    def get_chat_chat_logs(self,chat_id:str):
        return self.chats_logs.get_chat_logs(chat_id)

    def add_new_chat_log(self,chat_id:str, prompt:str,response:str):
        return self.chats_logs.create_chat_log(chat_id,prompt,response)

    def get_all_chats(self):
        return self.chats.get_all_chats()

    def get_all_chats_with_logs(self):
        chats = self.chats.get_all_chats()
        chat_ids = [item['chat_id'] for item in chats]
        all_chats_with_logs = [self.get_chat_with_logs(chat_id) for chat_id in chat_ids]
        return all_chats_with_logs

    def get_chat_with_logs(self,chat_id:str):
        self.chats_logs.get_chat_logs(chat_id)
        chat = self.chats.get_chat(chat_id)
        if chat:
            logs = self.get_chat_chat_logs(chat_id)
            chat_details = {
                'chat_id': chat_id,
                'title': chat['title'],
                'date': chat['date'],
                'logs':logs if logs else []
            }            
            return chat_details
        
    def delete_chat(self,chat_id:str):
        logs_deleted = self.chats_logs.delete_chat_logs(chat_id)
        if logs_deleted:
            chat_deleted = self.chats.delete_chat(chat_id)
            if chat_deleted:
                return True
        
    def delete_chat_logs(self,chat_id:str):
        return self.chats_logs.delete_chat_logs(chat_id)


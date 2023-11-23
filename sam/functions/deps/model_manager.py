import zipfile
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import shutil
import io
import botocore
from .logger import logger


class ModelManager:
    model = None
    tokenizer = None
    
    def __init__(self,s3,bucket_name,model_name,warm_up_key):
        self.s3 = s3
        self.s3_bucket = bucket_name
        self.model_name = model_name
        self.zip_key = "model_data.zip"
        self.model_key = "model_weights"
        self.tokenizer_key = "model_tokenizer_weights"

        self.local_path = "/tmp/model/"
        self.model_local_path = f"{self.local_path}model"
        self.tokenizer_local_path = f"{self.local_path}tokenizer"

        self.max_new_tokens = 1000
        if ModelManager.model and ModelManager.tokenizer:
            self.is_initialized = True
        else:
            self.is_initialized = False
        self.max_length_input = 10000

        self._temp_root = "/tmp"
        self._temp_root_dir = f"{self._temp_root}/model"
        self._temp_s3_model_path = f"{self._temp_root_dir}/model"
        self._temp_s3_tokenizer_path =  f"{self._temp_root_dir}/tokenizer"
        self.format = "zip"
        self.compress_name = "model"

        self.warm_up_key = warm_up_key
        self.completed_status_indicator = "completed"
        self.ongoing_status_indicator = "ongoing"
        self.fail_status_indicator = "failure"
        self.clean_status_indicator= "clean"
        

    def initialize_model(self):
        logger.info("func:initialize_model: Initialing Model")
        if ModelManager.model:
            logger.info("func:initialize_model: model already iniitialized")
            return

        if ModelManager.tokenizer:
            logger.info("func:initialize_model: tokenizer already iniitialized")
            return
        try:
            logger.info("func:initialize_model: get model zip")
            res = self.s3.get_object(Bucket=self.s3_bucket, Key=self.zip_key)
            logger.info("func:initialize_model: read model zip")
            zip_data = res['Body'].read()
            zip_buffer = io.BytesIO(zip_data)
            logger.info("func:initialize_model: extract model zip")
            with zipfile.ZipFile(zip_buffer,'r') as zip_ref:
                zip_ref.extractall(self.local_path)
            logger.info("func:initialize_model: iniitializing model and tokenizer class instances")
            ModelManager.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_local_path)
            ModelManager.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_local_path)
            self.is_initialized = True
        except Exception as e:
            logger.error("error in initialing model: %s",e)
    
    def upload_model(self):
        logger.info("func:upload_model: uploading model to s3...")
        try:
            self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=self.ongoing_status_indicator)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model.save_pretrained(self._temp_s3_model_path)
            tokenizer.save_pretrained(self._temp_s3_tokenizer_path)
            path = shutil.make_archive(self._temp_root + self.compress_name,self.format,root_dir=self._temp_root_dir)
            self.s3.upload_file(Filename=path, Bucket=self.s3_bucket, Key=self.zip_key)
            self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=self.completed_status_indicator)
            res = {
                "status": self.completed_status_indicator
            }
            return res
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error in upload_model: {e}")
            res = {
                "err": str(e),
            }
            return res
        except Exception as e:
            logger.error(f"Error in upload_model: {e}")
            self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=self.fail_status_indicator)
            res = {
                "status": self.fail_status_indicator,
            }
            return res

    def _handle_input(self,text_inputs):
        logger.info("func:_handle_input:handle input")
        model_input = '' 

        if isinstance(text_inputs,list):
            history_size = len(text_inputs)
            if history_size > 1:
                history_sizes = reversed(text_inputs)
                acc = history_size
                prompt_history = []
                for s in history_sizes:
                    if acc + len(s) > self.max_length_input:
                        break
                    acc += len(s)
                    prompt_history.append(s)
                model_input = " ".join(reversed(prompt_history))
            else:
                model_input = text_inputs[0]
                if len(model_input) > self.max_length_input:
                    model_input =  model_input[-self.max_length_input:]

        if isinstance(text_inputs,str):
            model_input = text_inputs
            if len(model_input) > self.max_length_input:
                model_input =  model_input[-self.max_length_input:]            

        return model_input

    def _prepare_model_input(self,text):
        logger.info("func:_prepare_model_input:Prepare Model Input")
        return text

    def predict_title(self,text_input:str):
        logger.info("func:predict_title: Generating title for chat by first prompt...")
        title_prompt_input = self._handle_input(text_input)
        title_prompt = f'please give a title for the following prompt "{title_prompt_input}"'
        model_input = self._prepare_model_input(title_prompt)
        res = self._predict(model_input)
        logger.debug(res)
        if isinstance(res, list):
            res = " ".join(res)
        if res is None:
            res = ''
        return res

    def _predict(self,text_inputs,max_new_tokens=None):
        logger.info("func:_predict: Predicting ...")
        max_tokens = max_new_tokens if max_new_tokens else self.max_new_tokens
        if not ModelManager.tokenizer:
            logger.info("func:_predict: No Tokenizer ...")
        if not ModelManager.model:
            logger.info("func:_predict: No Model ...")
        try:
            inputs = ModelManager.tokenizer(text_inputs, return_tensors="pt")
            outputs = ModelManager.model.generate(**inputs,max_new_tokens=max_tokens)
            response = ModelManager.tokenizer.batch_decode(outputs, skip_special_tokens=True)
            logger.info("func:_predict: successful prediction")
            return response
        except Exception as e:
            logger.error(f"func:_predict: error in predicting: {e}")
            logger.debug(inputs)
            
    def predict_prompt(self,text_inputs,max_new_tokens=None):
        logger.info("func:predict_prompt: Predicting Prompt...")
        model_input = self._prepare_model_input(self._handle_input(text_inputs))
        res = self._predict(model_input,max_new_tokens)
        if isinstance(res, list):
            res = " ".join(res)
        if res is None:
            res = ''
        logger.debug(res)
        return res

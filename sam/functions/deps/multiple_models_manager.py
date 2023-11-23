import zipfile
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import shutil
import io
import botocore
from .logger import logger
from .singleton_base import SingletonBase
from .utils import s3,LLMConfiguration,get_available_model,get_model_bucket_name,get_available_models,get_warm_up_key

   
class ModelsManager(SingletonBase):
    llm = None 

    @classmethod
    def upload_all_models(cls):
        for conf in get_available_models():
            LLMLoader(s3,conf).upload_model()

    @classmethod
    def set_model(cls,model_name):
        model_conf = get_available_model(model_name)
        result_tuple = LLMLoader(s3,model_conf).initialize_model()
        
        if isinstance(result_tuple, tuple) and len(result_tuple) == 2:
            model, tokenizer = result_tuple        
            llm = LLM(model,tokenizer,model_conf)
            cls.llm = llm

        else:
            logger.error("LLMLoader did not return the expected tuple (model, tokenizer)")

    @classmethod
    def get_model(cls):
        if isinstance(cls.llm,LLM):
            return cls.llm
        raise Exception("NOT LLM type:", type(cls.llm))

class LLM:

    def __init__(self,model,tokenizer,config:LLMConfiguration) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.config = config

    def _handle_input(self,text_inputs):
        logger.info(f"func:_handle_input:{self.config.model_name}")
        model_input = '' 

        if isinstance(text_inputs,list):
            history_size = len(text_inputs)
            if history_size > 1:
                history_sizes = reversed(text_inputs)
                acc = history_size
                prompt_history = []
                for s in history_sizes:
                    if acc + len(s) > self.config.max_length_input:
                        break
                    acc += len(s)
                    prompt_history.append(s)
                model_input = " ".join(reversed(prompt_history))
            else:
                model_input = text_inputs[0]
                if len(model_input) > self.config.max_length_input:
                    model_input =  model_input[-self.config.max_length_input:]

        if isinstance(text_inputs,str):
            model_input = text_inputs
            if len(model_input) > self.config.max_length_input:
                model_input =  model_input[-self.config.max_length_input:]            

        return model_input

    def _prepare_model_input(self,text):
        logger.info(f"func:_prepare_model_input:{self.config.model_name}")
        # config transform func
        return text

    def predict_title(self,text_input:str):
        logger.info(f"func:predict_title: Generating title for chat by first prompt with {self.config.model_name}... ")
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
        logger.info(f"func:_predict: Predicting with {self.config.model_name} ...")
        max_tokens = max_new_tokens if max_new_tokens else self.config.max_new_tokens
        try:
            inputs = self.tokenizer(text_inputs, return_tensors="pt")
            outputs = self.model.generate(**inputs,max_new_tokens=max_tokens)
            response = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
            return response
        except Exception as e:
            logger.error(f"func:_predict: error in predicting with {self.config.model_name}: {e}")
            logger.debug(text_inputs)
            
    def predict_prompt(self,text_inputs,max_new_tokens=None):   
        logger.info(f"func:predict_prompt: Predicting Prompt with {self.config.model_name}...  ")
        model_input = self._prepare_model_input(self._handle_input(text_inputs))
        res = self._predict(model_input,max_new_tokens)
        if isinstance(res, list):
            res = " ".join(res)
        if res is None:
            res = ''
        logger.debug(res)
        return res


class LLMLoader:
    
    def __init__(self,s3,config:LLMConfiguration):
        self.s3 = s3
        self.model_name = config.model_name
        self.model_key = config.model_key
        self.s3_bucket = get_model_bucket_name(self.model_name)
        self.zip_key = f"{self.model_key}_data.zip"
        self.model_weights_key = f"{self.model_key}_weights"
        self.tokenizer_key = f"{self.model_key}_tokenizer_weights"

        self.local_path = f"/tmp/model/"
        self.model_local_path = f"{self.local_path}model"
        self.tokenizer_local_path = f"{self.local_path}tokenizer"

        self._temp_root = "/tmp"
        self._temp_root_dir = f"{self._temp_root}/{self.model_key}"
        self._temp_s3_model_path = f"{self._temp_root_dir}/model"
        self._temp_s3_tokenizer_path =  f"{self._temp_root_dir}/tokenizer"
        self.format = "zip"
        self.compress_name = f"{self.model_key}"

        self.warm_up_key = get_warm_up_key(self.model_key)
        self.completed_status_indicator = "completed"
        self.ongoing_status_indicator = "ongoing"
        self.fail_status_indicator = "failure"
        self.clean_status_indicator= "clean"

    def initialize_model(self):
        logger.info(f"func:initialize_model: Initialing {self.model_name}")
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
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_local_path)
            self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_local_path)

            self.is_initialized = True
            return self.model,self.tokenizer
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
            res = self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=self.completed_status_indicator)
            logger.debug(res)
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



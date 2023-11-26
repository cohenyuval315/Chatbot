import zipfile
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import shutil
import io
import botocore
from .logger import logger
from .singleton_base import SingletonBase
from .utils import s3,LLMConfiguration,get_available_model,get_model_bucket_name,get_warm_up_key,MODEL_AVAILABLE_OPTIONS,ONGOING_STATUS_INDICATOR,CLEAN_STATUS_INDICATOR,COMPLETED_STATUS_INDICATOR,FAIL_STATUS_INDICATOR,OVERWRITE_MODELS
from .execptions import *
import torch


class ModelsManager(SingletonBase):
    llm = None 

    @classmethod
    def upload_all_models(cls):
        for conf in MODEL_AVAILABLE_OPTIONS:
            LLMUploader(s3,conf,OVERWRITE_MODELS).upload_model()

    @classmethod
    def set_model(cls,model_name,task=None):
        try:
            model_conf = get_available_model(model_name)
            result_tuple = LLMLoader(s3,model_conf).initialize_model()
            model, tokenizer = result_tuple        
            llm = LLM(model,tokenizer,model_conf, task)
            cls.llm = llm        
        except Exception as e:
            raise ModelsManagerError from e

    @classmethod
    def get_model(cls):
        if isinstance(cls.llm,LLM):
            return cls.llm
        raise ModelsManagerError from TypeError("model manager llm must be LLM type")


class LLM:

    def __init__(self,model,tokenizer,config:LLMConfiguration,task=None) -> None:
        self.model = model
        self.tokenizer = tokenizer
        try:
            self.model_max_length = self.tokenizer.model_max_length
            logger.debug(f"{self.model_max_length}")
        except:
            pass
            
        self.no_grad = False
        self.config = config
        self.task = task
        
    def __handle_list_strings(self,list_of_strs:list[str]):
        size = len(list_of_strs)
        if size > 1:
            reversed_lst = reversed(list_of_strs)
            accumelator = size # 0 + size * len(" ") =  size  // " ".join
            items = []
            for s in reversed_lst:
                if accumelator + len(s) > self.config.max_length_input:
                    break
                accumelator += len(s)
                items.append(s)
            string_input = " ".join(reversed(items))    
        else:
            string_input = list_of_strs[0]
            if len(string_input) > self.config.max_length_input:
                string_input =  string_input[-self.config.max_length_input:]            
        return string_input                
    
    def __handle_list_dict(self,list_of_dicts:list[dict]):
        return list_of_dicts
    
    def __handle_string_input(self,string:str):
        string_input = string
        if len(string_input) > self.config.max_length_input:
            string_input =  string_input[-self.config.max_length_input:]            
        return string_input

    def _handle_input(self,text_inputs):

        if isinstance(text_inputs,list):
            history_size = len(text_inputs)
            if history_size < 1:
                raise Exception("Model Empty List Input Error")
            if isinstance(text_inputs[0], dict):
                return self.__handle_list_dict(text_inputs)
            if isinstance(text_inputs[0], str):
                return self.__handle_list_strings(text_inputs)
            raise Exception("Model List Type Error")
        
        if isinstance(text_inputs,str):
            return self.__handle_string_input(text_inputs)
        
        raise Exception("Model Input Type Error")

    def _prepare_model_input(self,text):
        return text


    def get_title_prompt(self,title_prompt_input):
        title_prompt = f'please give a title for the following prompt "{title_prompt_input}"'
        return title_prompt

    def predict_title(self,text_input:str):
        title_prompt_input = self._handle_input(text_input)
        title_prompt = self.get_title_prompt(title_prompt_input)
        model_input = self._prepare_model_input(title_prompt)
        res = self.predict(model_input)
        return res

    def predict_prompt(self,text_inputs,max_new_tokens=None):   
        text_input = self._handle_input(text_inputs)
        model_input = self._prepare_model_input(text_input)
        res = self.predict(model_input,max_new_tokens)
        return res

    def predict(self,text_inputs,max_new_tokens=None,skip_special_token=True):
        inputs = self.tokenize(text_inputs)
        output = self.generate(inputs,max_new_tokens)
        predict_result = self.clean_batch_decode(output,skip_special_token=skip_special_token)
        results = self.handle_results(predict_result)
        return results
           
    def generate(self,inputs, max_new_tokens=None):  
        max_tokens = max_new_tokens if max_new_tokens else self.config.max_new_tokens
        if self.no_grad:
            with torch.no_grad():
                output = self.model.generate(**inputs,max_new_tokens=max_tokens)
        else:
            output = self.model.generate(**inputs,max_new_tokens=max_tokens)
        return output

    def tokenize(self,text_inputs):
        tokens = self.tokenizer(
            text_inputs, 
            return_tensors="pt")
        return tokens

    def batch_decode(self,output):
        response = self.tokenizer.batch_decode(output, False)
        return response
    
    def clean_batch_decode(self,output):
        response = self.tokenizer.batch_decode(output,True)
        return response    
    
    def handle_results(self,predicted_result):
        final_result = predicted_result
        if final_result is None or len(final_result) == 0:
            raise LLMError("Prediction Error",debug=final_result)
        if isinstance(final_result,list):
            final_result = " ".join(final_result)
        return final_result
    


class LLMHandler:
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
        self.completed_status_indicator = COMPLETED_STATUS_INDICATOR
        self.ongoing_status_indicator = ONGOING_STATUS_INDICATOR
        self.fail_status_indicator = FAIL_STATUS_INDICATOR
        self.clean_status_indicator= CLEAN_STATUS_INDICATOR

        self.is_initialized = False


class LLMUploader(LLMHandler):
    def __init__(self, s3, config: LLMConfiguration,overwrite=False):
        self.overwrite = overwrite
        super().__init__(s3, config)

    def load_model(self):
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

    def load_tokenizer(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
       
    def _temp_save_model(self):
        self.model.save_pretrained(self._temp_s3_model_path)

    def _temp_save_tokenizer(self):
        self.tokenizer.save_pretrained(self._temp_s3_tokenizer_path)

    def make_archive(self):
        self.path = shutil.make_archive(self._temp_root + self.compress_name, self.format, root_dir=self._temp_root_dir)

    def upload_archive(self):
        self.s3.upload_file(Filename=self.path, Bucket=self.s3_bucket, Key=self.zip_key)

    def update_warm_up_key(self,status_indicator):        
        self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=status_indicator)

    def is_archive_loaded(self):
        try:
            self.s3.head_object(Bucket=self.s3_bucket, Key=self.zip_key)
            return True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.warning(e)
                return False

    def upload_model(self):
        try:
            if not self.overwrite:
                is_exists = self.is_archive_loaded()
                logger.debug(is_exists)
                if is_exists:
                    return
            self.update_warm_up_key(self.ongoing_status_indicator)
            self.load_model()
            self.load_tokenizer()
            self._temp_save_model()
            self._temp_save_tokenizer()
            self.make_archive()
            self.upload_archive()
            self.update_warm_up_key(self.completed_status_indicator)
        except Exception as ex:
            try:
                self.update_warm_up_key(self.fail_status_indicator)
            except Exception as e:
                raise (LLMCleanUpError,LLMError) from e
            raise LLMError from ex
        
    def upload_model_old(self):
        # logger.info("func:upload_model: uploading model to s3...")
        try:
            self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=self.ongoing_status_indicator)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model.save_pretrained(self._temp_s3_model_path)
            tokenizer.save_pretrained(self._temp_s3_tokenizer_path)
            path = shutil.make_archive(self._temp_root + self.compress_name,self.format,root_dir=self._temp_root_dir)
            self.s3.upload_file(Filename=path, Bucket=self.s3_bucket, Key=self.zip_key)
            res = self.s3.put_object(Bucket=self.s3_bucket, Key=self.warm_up_key, Body=self.completed_status_indicator)
            # logger.debug(res)
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


class LLMLoader(LLMHandler):
    
    def __init__(self, s3, config: LLMConfiguration):
        super().__init__(s3, config)

    def initialize_model(self):
        if self.is_initialized:
            return self.model,self.tokenizer    
        self.download_model()
        self.extract_model()
        self.load_model_from_path()
        self.load_tokenizer_from_path()
        self.is_initialized = True
        return self.model,self.tokenizer
    
    def initialize_model_old(self):
        # logger.info(f"func:initialize_model: Initialing {self.model_name}")
        try:
            # logger.info("func:initialize_model: get model zip")
            res = self.s3.get_object(Bucket=self.s3_bucket, Key=self.zip_key)
            # logger.info("func:initialize_model: read model zip")
            zip_data = res['Body'].read()
            zip_buffer = io.BytesIO(zip_data)
            # logger.info("func:initialize_model: extract model zip")
            with zipfile.ZipFile(zip_buffer,'r') as zip_ref:
                zip_ref.extractall(self.local_path)
            # logger.info("func:initialize_model: iniitializing model and tokenizer class instances")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_local_path)
            self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_local_path)

            self.is_initialized = True
            return self.model,self.tokenizer
        except Exception as e:
            logger.error("error in initialing model: %s",e)
    
    def download_model(self):
        self.model_object = self.s3.get_object(Bucket=self.s3_bucket, Key=self.zip_key)

    def extract_model(self):
        zip_data = self.model_object['Body'].read()
        zip_buffer = io.BytesIO(zip_data)
        with zipfile.ZipFile(zip_buffer,'r') as zip_ref:
            zip_ref.extractall(self.local_path)

    def load_model_from_path(self):
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_local_path)
     
    def load_tokenizer_from_path(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_local_path)


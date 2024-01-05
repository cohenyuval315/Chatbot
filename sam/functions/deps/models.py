
import dataclasses
from .config import *
from typing import Optional
import enum

class TaskType(enum.Enum):
    DEFAULT = "default"
    QA = "QuestionAnswer"
    SUM = "summarization"


@dataclasses.dataclass
class LLMConfiguration:

    model_name:str
    model_key:str
    max_length_input:int
    max_new_tokens:Optional[int]
    model_link: Optional[str] = None
    tasks: Optional[list[TaskType]] = None
    trainable:bool = False

    # 
    max_length:int = 20
    min_length:int = 0 
    min_new_tokens:Optional[int] = None 
    max_time:Optional[float] = None
    early_stopping:Optional[str] = False 
 

    def to_json(self): 
        res =  {
            "model_name":self.model_name,
            "model_key":self.model_key,
            "max_length_input":self.max_length_input,
            "max_new_tokens":self.max_new_tokens,
            'trainable':self.trainable
        }
        if self.model_link:
            res['model_link'] = self.model_link
        if self.model_link:
            res['tasks'] = [t.value for t in self.tasks]  
        return res
    

    def to_user_json(self): # return to user
        res =  {
            "model_name":self.model_name,
            "model_key":self.model_key,
            "max_length_input":self.max_length_input,
            "max_new_tokens":self.max_new_tokens,
            'trainable':self.trainable
        }
        if self.model_link:
            res['model_link'] = self.model_link
        if self.model_link:
            res['tasks'] = [t.value for t in self.tasks]            
        return res
    


flan_t5_small = LLMConfiguration(
    model_name="google/flan-t5-small",
    model_key="flan_t5_small",
    max_length_input=10000,
    max_new_tokens=1000,
    model_link="https://huggingface.co/google/flan-t5-small",
    tasks=[TaskType.DEFAULT,TaskType.QA,TaskType.SUM],
    trainable=False
    )

flan_t5_base = LLMConfiguration(
    model_name="google/flan-t5-base",
    model_key="flan_t5_base",
    max_length_input=10000,
    max_new_tokens=1000,
    model_link="https://huggingface.co/google/flan-t5-base",
    tasks=[TaskType.DEFAULT,TaskType.QA,TaskType.SUM],
    trainable=False
    )

MODEL_OPTIONS = [
    flan_t5_small,
    flan_t5_base
]

MODEL_AVAILABLE_OPTIONS_INDEXES = [0,1]
MODEL_AVAILABLE_OPTIONS = []
for model_option_index in MODEL_AVAILABLE_OPTIONS_INDEXES:
    MODEL_AVAILABLE_OPTIONS.append(MODEL_OPTIONS[model_option_index])


OVERWRITE_MODELS = False





from .logger import logger
import traceback

class ExceptionBase(Exception):
    def __init__(self, default_message:str, message=None,debug=None,verbose:bool=True):
        self.message =  message or default_message
        self.verbose = verbose
        self.debug = debug
        
        logger.error(f"{self.message}")
        if debug:
            logger.debug(debug)
        super().__init__(self.message)

    def __str__(self):
        if self.verbose:
            return "".join(traceback.format_stack()[:-1])
        else:
            return f"{self.message}"        

class ServerlessException(ExceptionBase):
    def __init__(self, default_message=None, message=None, debug=None, verbose: bool = True):
        base_default_message = default_message if default_message else "Serverless Error"
        super().__init__(base_default_message, message, debug, verbose)

class LLMError(ServerlessException):
    def __init__(self, message=None, debug=None, verbose: bool = True):
        default_message = "LLM Error"
        super().__init__(default_message, message, debug, verbose)

class LLMUploaderError(ServerlessException):
    def __init__(self, message=None, debug=None, verbose: bool = True):
        default_message = "LLM Uploader Error"
        super().__init__(default_message, message, debug, verbose)

class LLMLoaderError(ServerlessException):
    def __init__(self, message=None, debug=None, verbose: bool = True):
        default_message = "LLM Loader Error"
        super().__init__(default_message, message, debug, verbose)

class LLMCleanUpError(ServerlessException):
    def __init__(self, message=None, debug=None, verbose: bool = True):
        default_message = "LLM Clean Up Error"
        super().__init__(default_message, message, debug, verbose)

class ModelsManagerError(ServerlessException):
    def __init__(self, default_message: str, message=None, debug=None, verbose: bool = True):
        super().__init__(default_message, message, debug, verbose)

class DynamoDBError(ServerlessException):
    def __init__(self, default_message: str, message=None, debug=None, verbose: bool = True):
        super().__init__(default_message, message, debug, verbose)

class ClientException(ExceptionBase):
    def __init__(self, default_message=None, message=None, debug=None, verbose: bool = True):
        base_default_message = default_message if default_message else "Client Error"
        super().__init__(base_default_message, message, debug, verbose)





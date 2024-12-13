from .base import BaseException

class JSONFileNotFoundError(BaseException):
    def __init__(self, file_path: str):
        super().__init__(f" json file '{file_path}' not found.", None, 200)
        
class InvalidJSONFormatError(BaseException):
    def __init__(self, file_path: str, cause=None):
        super().__init__(f"Invalid JSON format in file '{file_path}'.", cause, 201)
        
class MissingKeyError(BaseException):
    def __init__(self, key: str, file_path: str):
        super().__init__(f"Missing required key '{key}' in JSON file '{file_path}'.", None, 202)

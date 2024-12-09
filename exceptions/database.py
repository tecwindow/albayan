from .base import BaseException

class DBNotFoundError(BaseException):
    def __init__(self, db_path: str):
        super().__init__(f"Database not found at path: {db_path}", None, 101)

class InvalidCriteriaError(BaseException):
    def __init__(self, criteria: str):
        super().__init__(f"Invalid search criteria: '{criteria}'", None, 102)

class DatabaseConnectionError(BaseException):
    def __init__(self, message: str = "", cause=None):
        super().__init__(f"Failed to connect to the database: {message}", cause, 103)

class InvalidSearchTextError(BaseException):
    def __init__(self, search_text):
        super().__init__(f"Invalid search text: '{search_text}'", None, 104)


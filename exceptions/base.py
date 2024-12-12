from abc import ABC, abstractmethod
from utils.const import Globals


class BaseException(ABC, Exception):
    """
    Abstract base class for custom exceptions. 
    Ensures consistency by requiring message, cause, and code attributes.
    """
    def __init__(self, message: str = "An error occurred", cause: Exception = None, code: int = 0):
        """
        :param message: A descriptive message for the exception.
        :param cause: The underlying cause of the exception (optional).
        :param code: A unique code identifying the type of the exception.
        """
        super().__init__(message)
        self.message = message
        self.cause = cause
        self.code = code

    def __str__(self):
        """Convert the object into readable text."""
        base_message = f"[Error Code: {self.code}] {self.message}"
        if self.cause:
            base_message += f" | Cause: {repr(self.cause)}"
        return base_message

class ErrorMessage:
    def __init__(self, exception: Exception):
        self.exception = exception


    def get_code(self) -> int:
        return getattr(self.exception, "code", None)

    @property
    def title(self) -> str:
        return "خطأ"

    @property
    def body(self) -> str:
        Globals.effects_manager.play("error")
        body = "حدث خطأ، إذا استمرت المشكلة، يرجى تفعيل السجل وتكرار الإجراء الذي تسبب بالخطأ ومشاركة رمز الخطأ والسجل مع المطورين."
        code = self.get_code()
        if code:
            body += f"\nرمز الخطأ: {code}"
        return body

    @property
    def log_message(self) -> str:
        code = self.get_code()
        error_type = type(self.exception).__name__
        error_message = str(self.exception)
        return f"Error Type: {error_type}, Code: {code or 'N/A'}, Message: {error_message}"

    def __str__(self) -> str:
        return self.log_message


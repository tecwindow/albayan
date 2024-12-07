from abc import ABC, abstractmethod

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



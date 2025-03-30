from functools import wraps
from .base import ErrorMessage
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

def exception_handler(func=None, *, ui_element=None, exception_types=(Exception,)):
    """
    General decorator to handle exceptions in a specific context.

    Args:
        func: The function being decorated.
        ui_element: UI element (e.g., QLabel, QMessageBox) to display error messages, or None.
        exception_types: Tuple of exception classes to catch. Defaults to (Exception,).
    """
    if func is None:
        # Allow decorator to be used with or without arguments
        return lambda f: exception_handler(f, ui_element=ui_element, exception_types=exception_types)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exception_types as e:
            # Create and log the error message
            message = ErrorMessage(e)
            logger.error(message.log_message, exc_info=True)

            # Handle UI element display
            if ui_element:
                if hasattr(ui_element, "critical"):
                    ui_element.critical(None, message.title, message.body)
                elif hasattr(ui_element, "setText"):
                    ui_element.setText(f"{message.title}: {message.body}")
                else:
                    logger.warning("UI element provided does not support error display.")

    return wrapper

import logging
from functools import wraps
from exceptions.audio_pplayer import (
    AudioFileNotFoundError, LoadFileError, InvalidSourceError,
    UnsupportedFormatError, PlaybackControlError, 
)

def exception_handler(ui_element=None, exception_types=(Exception,), default_message="An error occurred"):
    """
    General decorator to handle exceptions in a specific context.

    Args:
        ui_element: UI element (e.g., QLabel, QMessageBox) to display error messages, or None.
        exception_types: Tuple of exception classes to catch. Defaults to (Exception,).
        default_message: Default error message if no specific message is provided.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):  
            error_code = None
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                # Extract message and code if available
                error_message = str(e) 
                error_code = getattr(e, "code", None)  
            except Exception as e:
                error_message = str(e)  

            # Default message and error handling
            if error_code is not None:
                # If there's a specific error code, append it to the message
                message = f"{default_message}\nرمز الخطأ: {error_code}"
            else:
                # If no code, just show the default message
                message = default_message

            # Handle UI element display (show the error message to the user)
            if ui_element:
                if hasattr(ui_element, "critical"):
                    ui_element.critical(None, "خطأ", message)

            # Log error 
            logging.error(f"Error {error_code} in {func.__name__}: {error_message}", exc_info=True)

        return wrapper
    return decorator

def player_exception_handler(ui_element=None):
    """
    Handles exceptions related to the audio player.
    """
    return exception_handler(
        ui_element=ui_element, 
        exception_types=(AudioFileNotFoundError, LoadFileError, UnsupportedFormatError, InvalidSourceError, PlaybackControlError),
        default_message="حدث خطأ أثناء تشغيل الملف."
    )

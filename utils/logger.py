import logging
import traceback
import ctypes
import os
import sys
from enum import Enum


class LogLevel(Enum):
    DISABLE = -1
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    #CRITICAL = logging.CRITICAL

    @classmethod
    def get_labels(cls) -> dict:
        """Returns a dictionary mapping log levels to their labels."""
        return {
            cls.DISABLE: "تعطيل",
            cls.DEBUG: "تصحيح (Debug)",
            cls.INFO: "معلومات (Info)",
            cls.WARNING: "تحذير (Warning)",
            cls.ERROR: "خطأ (Error)",
        }

    @property
    def label(self):
        """Returns the label for the log level."""
        return self.get_labels()[self]

    @classmethod
    def from_name(cls, name):
        """
        Retrieves the log level enum member corresponding to the given English name.
        
        Args:
            name (str): The English name of the log level (e.g., "DEBUG").
        
        Returns:
            LogLevel: The matching log level enum member.
        """
        return cls[name]
    
class LoggerManager:
    _initialized = False

    @classmethod
    def setup_logger(cls, log_file: str, log_level: LogLevel = LogLevel.ERROR, dev_mode=False):
        """
        Configures the root logger with file and (optionally) console handlers using basicConfig.
        Each handler gets its own formatter.
        
        :param log_file: Path to the log file.
        :param log_level: The logging level.
        :param dev_mode: If True, adds a console handler for development.
        """
        
        if not isinstance(log_level, LogLevel):
            raise ValueError("log_level must be an instance of LogLevel")
        
        if not cls._initialized:
            handlers = []
            # Organize handlers using the dedicated methods
            handlers.append(cls._get_file_handler(log_file, log_level))
            if dev_mode:
                handlers.append(cls._get_console_handler(log_level))
            
            logging.basicConfig(
                level=log_level.value,
                handlers=handlers
            )
            cls._initialized = True

    @classmethod
    def _get_file_handler(cls, log_file: str, log_level: LogLevel):
        """
        Creates and returns a FileHandler with its specific formatter.
        
        :param log_file: The file path for logging output.
        :param log_level: Logging level for the handler.
        :return: A list containing a configured FileHandler.
        """
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level.value)
        # File handler formatter (detailed format)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(filename)s:%(lineno)d]'
        )
        file_handler.setFormatter(file_formatter)
        return file_handler

    @classmethod
    def _get_console_handler(cls, log_level: LogLevel):
        """
        Creates and returns a console (Stream) handler with its specific formatter.
        
        :param log_level: Logging level for the handler.
        :return: A configured StreamHandler.
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level.value)
        # Console handler formatter (simplified format)
        console_formatter = logging.Formatter(
            '%(name)s - %(levelname)s - %(message)s [in %(filename)s:%(lineno)d]'
        )
        console_handler.setFormatter(console_formatter)
        return console_handler

    @classmethod
    def change_log_level(cls, new_level: LogLevel):
        """
        Dynamically changes the log level for the root logger and its handlers.
        
        args:
        new_level (LogLevel): The new log level to set.
        
        Raises:
        ValueError: If new_level is not an instance of LogLevel.
        """

        if not isinstance(new_level, LogLevel):
            raise ValueError("new_level must be an instance of LogLevel")
        
        if new_level == LogLevel.DISABLE:
            logging.disable(logging.CRITICAL + 1)
            return
        else:
            # Enable all logging levels
            logging.disable(logging.NOTSET)  

        root_logger = logging.getLogger()
        root_logger.setLevel(new_level.value)
        for handler in root_logger.handlers:
            handler.setLevel(new_level.value)

    @classmethod
    def get_logger(cls, name):
        """
        Retrieves a logger by name.
        
        :param name: Name of the logger.
        :return: Logger instance.
        """
        return logging.getLogger(name)

    @staticmethod
    def show_error_message(message:str) -> None:
        ctypes.windll.user32.MessageBoxW(None, message, "Error", 0x10)

    @classmethod
    def my_excepthook(cls, exctype, value, tb):
        tb_list = traceback.extract_tb(tb)
        error_message = "Exception Type: {} | ".format(exctype.__name__)

        for tb in tb_list:
            file_name = os.path.basename(tb.filename)
            line_number = tb.lineno
            code = tb.line

            error_message += "File: {} | Line: {} | Code: {} | ".format(file_name, line_number, code)

        error_message += "Error Value: {}".format(value)
        logging.error(error_message, exc_info=True)
        cls.show_error_message("حدث خطأ، إذا استمرت المشكلة، يرجى تفعيل السجل وتكرار الإجراء الذي تسبب بالخطأ ومشاركة رمز الخطأ والسجل مع المطورين.")

import logging
import traceback
import ctypes
import os
import sys
from enum import Enum


class LogLevel(Enum):
    DISABLE = 0
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    #CRITICAL = logging.CRITICAL

    LABELS = {
        DISABLE: "تعطيل",
        DEBUG: "تصحيح (Debug)",
        INFO: "معلومات (Info)",
        WARNING: "تحذير (Warning)",
        ERROR: "خطأ (Error)",
        #CRITICAL: "حرج (Critical)"
    }

    @property
    def label(self):
        """Returns the label for the log level."""
        return self.LABELS[self]

    @classmethod
    def get_labels(cls):
        """Returns a dictionary mapping each log level name to its label."""
        return {level.name: level.label for level in cls}

    @classmethod
    def from_label(cls, label):
        """
        Retrieves the log level enum member corresponding to the given label.
        
        Args:
            label (str): The label for level.
        
        Returns:
            LogLevel: The matching log level enum member.
        
        Raises:
            ValueError: If no log level with the given label is found.
        """
        for level, lbl in cls.LABELS.items():
            if lbl == label:
                return level
        raise ValueError(f"Invalid log level label: {label}")

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
    def setup_logger(cls, log_file='app.log', log_level=logging.DEBUG, dev_mode=False):
        """
        Configures the root logger with file and (optionally) console handlers using basicConfig.
        Each handler gets its own formatter.
        
        :param log_file: Path to the log file.
        :param log_level: The logging level.
        :param dev_mode: If True, adds a console handler for development.
        """
        if not cls._initialized:
            # Organize handlers using the dedicated methods
            handlers = cls._get_file_handler(log_file, log_level)
            if dev_mode:
                handlers.append(cls._get_console_handler(log_level))
            
            logging.basicConfig(
                level=log_level,
                handlers=handlers
            )
            cls._initialized = True

    @classmethod
    def _get_file_handler(cls, log_file, log_level):
        """
        Creates and returns a FileHandler with its specific formatter.
        
        :param log_file: The file path for logging output.
        :param log_level: Logging level for the handler.
        :return: A list containing a configured FileHandler.
        """
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        # File handler formatter (detailed format)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(file_formatter)
        return [file_handler]

    @classmethod
    def _get_console_handler(cls, log_level):
        """
        Creates and returns a console (Stream) handler with its specific formatter.
        
        :param log_level: Logging level for the handler.
        :return: A configured StreamHandler.
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        # Console handler formatter (simplified format)
        console_formatter = logging.Formatter(
            '%(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        return console_handler

    @classmethod
    def change_log_level(cls, new_level):
        """
        Dynamically changes the log level for the root logger and its handlers.
        
        :param new_level: The new logging level (e.g., logging.ERROR).
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(new_level)
        for handler in root_logger.handlers:
            handler.setLevel(new_level)

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

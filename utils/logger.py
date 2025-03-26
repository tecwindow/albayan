import logging
import traceback
import os
import ctypes
import sys
from utils.settings import Config
from utils.const import albayan_folder


class Logger:
    log_file = os.path.join(albayan_folder, "albayan.log")
    last_logging_status = None

    @classmethod
    def initialize_logger(cls) -> None:
        current_logging_status = True  # Change to a boolean instead of string comparison
        if current_logging_status == cls.last_logging_status:
            return

        mode = "a" if current_logging_status else "w"
        logging.basicConfig(
            level=logging.INFO,
            format="(%(asctime)s) | %(name)s | %(levelname)s => '%(message)s'",
            handlers=[
                logging.FileHandler(cls.log_file, mode=mode, encoding="utf-8"),
                logging.StreamHandler()  # Also print logs to the console
            ]
        )

        cls.last_logging_status = current_logging_status  
        logging.info("Logger initialized successfully.")

    @classmethod
    def info(cls, message:str) -> None:
        cls.initialize_logger()
        if Config.general.logging_enabled:
            logging.info(message)

    @classmethod
    def error(cls, message:str) -> None:
        cls.initialize_logger()
        logging.error(message, exc_info=True)

    @classmethod
    def show_error_message(cls, message:str) -> None:
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

        cls.error(error_message)
        print(error_message)
        cls.show_error_message("حدث خطأ، إذا استمرت المشكلة، يرجى تفعيل السجل وتكرار الإجراء الذي تسبب بالخطأ ومشاركة رمز الخطأ والسجل مع المطورين.")

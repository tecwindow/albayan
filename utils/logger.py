import logging
import traceback
import os
import ctypes
import sys
from utils.settings import SettingsManager
from utils.const import albayan_folder


class Logger:
	last_logging_status = None

	@classmethod
	def initialize_logger(cls):
		current_logging_status = "True"
		if current_logging_status != cls.last_logging_status:
			if current_logging_status == "True":
				mode = "a"
			else:
				mode = "w"
			logging.basicConfig(filename=os.path.join(albayan_folder, "albayan.log"),
level=logging.INFO,
					filemode=mode,
					format="(%(asctime)s) | %(name)s | %(levelname)s => '%(message)s'")
		cls.last_logging_status = current_logging_status

	@classmethod
	def info(cls, message:str) -> None:
		cls.initialize_logger()
		if SettingsManager.current_settings["general"].get("is_logging_enabled"):
			logging.info(message)

	@classmethod
	def error(cls, message:str) -> None:
		cls.initialize_logger()
		logging.error(message)

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
		cls.show_error_message("حدث خطأ. يرجى الاتصال بالدعم للحصول على المساعدة.")

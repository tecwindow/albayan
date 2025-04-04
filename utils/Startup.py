import winreg as reg
import os
import sys
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class StartupManager:
    STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_path = f'"{os.path.abspath(sys.argv[0])}" --minimized'

    @staticmethod
    def add_to_startup(app_name: str) -> None:
        """
        Adds the application to the Windows startup registry.

        :param app_name: Name of the application (Registry key name).
        """
        logger.info(f"Adding {app_name} application to startup...")

        if not sys.argv[0].endswith(".exe"):
            logger.warning(f"Skipping startup registration: {sys.argv[0]} is not an .exe file.")
            return

        if StartupManager.is_in_startup(app_name):
            logger.info(f"{app_name} is already in startup.")
            return

        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, StartupManager.STARTUP_KEY, 0, reg.KEY_SET_VALUE) as registry_key:
                reg.SetValueEx(registry_key, app_name, 0, reg.REG_SZ, StartupManager.app_path)
                logger.info(f"{app_name} added to startup successfully at {StartupManager.app_path}.")
        except WindowsError as e:
            logger.error(f"Failed to add {app_name} to startup: {e}", exc_info=True)

    @staticmethod
    def remove_from_startup(app_name: str) -> None:
        """Removes the application from the Windows startup registry."""
        logger.info(f"Removing {app_name} application from startup...")
        
        if not StartupManager.is_in_startup(app_name):
            logger.info(f"{app_name} is not in startup.")
            return

        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, StartupManager.STARTUP_KEY, 0, reg.KEY_SET_VALUE) as registry_key:
                reg.DeleteValue(registry_key, app_name)
                logger.info(f"{app_name} removed from startup successfully.")
        except FileNotFoundError:
            logger.error(f"{app_name} not found in startup.", exc_info=True)
        except WindowsError as e:
            logger.error(f"Failed to remove {app_name} from startup: {e}", exc_info=True)

    @staticmethod
    def is_in_startup(app_name: str) -> bool:
        """Checks if the application is registered in the Windows startup registry."""
        logger.debug(f"Checking if {app_name} is in startup...")
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, StartupManager.STARTUP_KEY, 0, reg.KEY_READ) as registry_key:
                reg.QueryValueEx(registry_key, app_name)
                logger.debug(f"{app_name} is found in startup.")
                return True
        except FileNotFoundError:
            logger.debug(f"{app_name} is not found in startup.")
            return False
        except WindowsError as e:
            logger.error(f"Failed to check startup status: {e}", exc_info=True)
            logger.debug(f"{app_name} is not in startup.")
            return False

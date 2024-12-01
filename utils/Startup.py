import winreg as reg
import os
import sys
from utils.logger import Logger

class StartupManager:
    STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_path = f'"{os.path.abspath(sys.argv[0])}" --minimized'
    Logger.info(app_path)

    @staticmethod
    def add_to_startup(app_name: str) -> None:
        """
        Adds the application to the Windows startup registry.

        :param app_name: Name of the application (Registry key name).
        """
        if not sys.argv[0].endswith(".exe"):
            return

        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, StartupManager.STARTUP_KEY, 0, reg.KEY_SET_VALUE) as registry_key:
                reg.SetValueEx(registry_key, app_name, 0, reg.REG_SZ, StartupManager.app_path)
                Logger.info(f"{app_name} added to startup successfully.")
        except WindowsError as e:
            Logger.error(f"Failed to add {app_name} to startup: {e}")

    @staticmethod
    def remove_from_startup(app_name: str) -> None:
        """Removes the application from the Windows startup registry."""
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, StartupManager.STARTUP_KEY, 0, reg.KEY_SET_VALUE) as registry_key:
                reg.DeleteValue(registry_key, app_name)
                Logger.info(f"{app_name} removed from startup successfully.")
        except FileNotFoundError:
            Logger.error(f"{app_name} not found in startup.")
        except WindowsError as e:
            Logger.error(f"Failed to remove {app_name} from startup: {e}")

    @staticmethod
    def is_in_startup(app_name: str) -> bool:
        """Checks if the application is registered in the Windows startup registry."""
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, StartupManager.STARTUP_KEY, 0, reg.KEY_READ) as registry_key:
                reg.QueryValueEx(registry_key, app_name)
                return True
        except FileNotFoundError:
            return False
        except WindowsError as e:
            Logger.error(f"Failed to check startup status: {e}")
            return False
        
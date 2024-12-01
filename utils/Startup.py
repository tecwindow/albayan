import winreg as reg
import os

class StartupManager:
    STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

    @staticmethod
    def add_to_startup(app_name, app_path):
        """
        Adds the application to the Windows startup registry.

        :param app_name: Name of the application (Registry key name).
        :param app_path: Full path to the executable with arguments if necessary.
        """
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, StartupManager.STARTUP_KEY, 0, reg.KEY_SET_VALUE) as registry_key:
                reg.SetValueEx(registry_key, app_name, 0, reg.REG_SZ, app_path)
                print(f"{app_name} added to startup successfully.")
        except WindowsError as e:
            print(f"Failed to add {app_name} to startup: {e}")

    @staticmethod
    def remove_from_startup(app_name):
        """
        Removes the application from the Windows startup registry.

        :param app_name: Name of the application (Registry key name).
        """
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, StartupManager.STARTUP_KEY, 0, reg.KEY_SET_VALUE) as registry_key:
                reg.DeleteValue(registry_key, app_name)
                print(f"{app_name} removed from startup successfully.")
        except FileNotFoundError:
            print(f"{app_name} not found in startup.")
        except WindowsError as e:
            print(f"Failed to remove {app_name} from startup: {e}")

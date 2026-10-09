from typing import Optional
import winreg as reg
import os
import sys
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class StartupManager:
    STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

    @classmethod
    def get_exe_path(cls) -> str:
        """Returns the absolute path to the executable or script."""
        if getattr(sys, "frozen", False):
            return os.path.abspath(sys.executable)
        return os.path.abspath(sys.argv[0])

    @classmethod
    def get_app_path(cls) -> str:
        """Returns the startup command with quotes and --minimized flag."""
        return f'"{cls.get_exe_path()}" --minimized'

    @classmethod
    def is_exe(cls) -> bool:
        """Checks if the application is running as an executable."""
        if getattr(sys, "frozen", False):
            return True
        return sys.argv[0].lower().endswith(".exe")

    @classmethod
    def get_startup_value(cls, app_name: str) -> Optional[str]:
        """Gets the current command registered under app_name in the Run registry key."""
        for name in [app_name, app_name.lower()]:
            try:
                with reg.OpenKey(
                    reg.HKEY_CURRENT_USER, cls.STARTUP_KEY, 0, reg.KEY_READ
                ) as registry_key:
                    value, _ = reg.QueryValueEx(registry_key, name)
                    return str(value)
            except (FileNotFoundError, WindowsError):
                continue
        return None

    @classmethod
    def add_to_startup(cls, app_name: str) -> None:
        """
        Adds or updates the application in the Windows startup registry.

        :param app_name: Name of the application (Registry key name).
        """
        logger.info(f"Adding/updating {app_name} application in startup...")

        if not cls.is_exe():
            logger.warning(
                f"Skipping startup registration: {cls.get_exe_path()} is not an .exe file."
            )
            return

        target_cmd = cls.get_app_path()
        current_cmd = cls.get_startup_value(app_name)

        if current_cmd == target_cmd:
            logger.info(
                f"{app_name} is already registered in startup with correct path."
            )
            return

        try:
            with reg.OpenKey(
                reg.HKEY_CURRENT_USER, cls.STARTUP_KEY, 0, reg.KEY_SET_VALUE
            ) as registry_key:
                reg.SetValueEx(registry_key, app_name, 0, reg.REG_SZ, target_cmd)
                logger.info(
                    f"{app_name} registered in startup successfully: {target_cmd}"
                )
        except WindowsError as e:
            logger.error(
                f"Failed to add/update {app_name} in startup: {e}", exc_info=True
            )

    @classmethod
    def remove_from_startup(cls, app_name: str) -> None:
        """Removes the application from the Windows startup registry."""
        logger.info(f"Removing {app_name} application from startup...")
        removed_any = False
        try:
            with reg.OpenKey(
                reg.HKEY_CURRENT_USER, cls.STARTUP_KEY, 0, reg.KEY_SET_VALUE
            ) as registry_key:
                for name in [app_name, app_name.lower()]:
                    try:
                        reg.DeleteValue(registry_key, name)
                        logger.info(f"{name} removed from startup successfully.")
                        removed_any = True
                    except FileNotFoundError:
                        pass
        except WindowsError as e:
            logger.error(
                f"Failed to remove {app_name} from startup: {e}", exc_info=True
            )

        if not removed_any:
            logger.info(f"{app_name} was not found in startup.")

    @classmethod
    def is_in_startup(cls, app_name: str) -> bool:
        """Checks if the application is registered in the Windows startup registry."""
        return cls.get_startup_value(app_name) is not None
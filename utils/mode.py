import os
import sys

# Import the registry class from registry library
from .registry import registry, RegistryError

# The AppId defined in InnoSetup script
APP_ID = "{5BDDE425-E22F-4A82-AF2F-72AF71301D3F}"

def get_current_app_dir() -> str:
    """Helper to get the current running directory (handles PyInstaller/frozen states)."""
    if getattr(sys, 'frozen', False):
        # Running as a compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as a standard Python script
        return os.path.dirname(os.path.abspath(sys.argv[0]))

def is_installed(app_id: str = APP_ID) -> bool:
    """
    Check if the current application is running from its installed location
    using the unmodified nb_registry library.
    """
    current_path = os.path.normcase(os.path.normpath(get_current_app_dir()))
    
    # InnoSetup automatically appends '_is1' to the AppId in the registry
    inno_key = f"{app_id}_is1"

    # Possible installation registry paths for Current User, Local Machine and 32/64-bit nodes
    registry_paths = [
        f"HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{inno_key}",
        f"HKLM\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{inno_key}",
        f"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{inno_key}",
        f"HKCU\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{inno_key}"
    ]

    for path in registry_paths:
        install_dir = None
        try:
            # First, check for 'Inno Setup: App Path' which is highly specific
            install_dir = registry.read(path, "Inno Setup: App Path")
            # Fallback to standard 'InstallLocation' if the specific one is missing
            if not install_dir:
                install_dir = registry.read(path, "InstallLocation")
        except RegistryError:
            # If there's an issue accessing this specific key (e.g., permissions), skip to the next
            continue
        except Exception:
            continue

        if install_dir:
            install_dir = os.path.normcase(os.path.normpath(str(install_dir)))
            
            # The app is considered "installed" if the current process runs from within the install dir
            if current_path == install_dir or current_path.startswith(install_dir + os.sep):
                return True

    return False

def is_portable(app_id: str = APP_ID) -> bool:
    """
    Check if the current application is running as a portable version.
    """
    return not is_installed(app_id)


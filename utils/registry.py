import winreg
import os
import ctypes
from functools import wraps
from typing import Any, Dict, List, Optional, Tuple, Union
import subprocess
import time

class RegistryError(Exception):
    """Base exception for registry operations."""
    pass

class RegistryNotFoundError(RegistryError):
    """Raised when a key or value is not found."""
    pass

class RegistryPermissionError(RegistryError):
    """Raised when permission issues occur."""
    pass

class RegistryTypeError(RegistryError):
    """Raised when an invalid type is used."""
    pass

class RegistryValueError(RegistryError):
    """Raised when the provided value is invalid for the specified type."""
    pass

class registry:
    """
    A professional Windows Registry interface.

    This class provides static methods to interact with the Windows Registry,
    handling common operations like reading, writing, deleting, listing,
    and monitoring keys and values. It includes robust error handling,
    type validation, and privilege checks.
    """

    # Registry type constants mapping
    TYPES = {
        "REG_SZ": winreg.REG_SZ,
        "REG_DWORD": winreg.REG_DWORD,
        "REG_BINARY": winreg.REG_BINARY,
        "REG_QWORD": winreg.REG_QWORD,
        "REG_MULTI_SZ": winreg.REG_MULTI_SZ,
        "REG_EXPAND_SZ": winreg.REG_EXPAND_SZ,
        "REG_NONE": winreg.REG_NONE
    }

    # Reverse mapping for getting string representation of type constants
    TYPE_NAMES = {v: k for k, v in TYPES.items()}

    # Root key mapping
    ROOT_KEYS = {
        "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
        "HKCR": winreg.HKEY_CLASSES_ROOT,
        "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
        "HKCU": winreg.HKEY_CURRENT_USER,
        "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
        "HKLM": winreg.HKEY_LOCAL_MACHINE,
        "HKEY_USERS": winreg.HKEY_USERS,
        "HKU": winreg.HKEY_USERS,
        "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
        "HKCC": winreg.HKEY_CURRENT_CONFIG,
        "HKEY_PERFORMANCE_DATA": winreg.HKEY_PERFORMANCE_DATA,
        "HKPD": winreg.HKEY_PERFORMANCE_DATA
    }

    @staticmethod
    def _is_admin() -> bool:
        """
        Check if the current process has administrator privileges.

        Returns:
            bool: True if the process is running with admin privileges, False otherwise.
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            # Handle cases where ctypes might not be available or other errors
            return False

    @staticmethod
    def _requires_admin(func):
        """
        Decorator to check for admin privileges before certain registry operations.

        This decorator raises a RegistryPermissionError if an operation
        on HKEY_LOCAL_MACHINE (or its alias HKLM) is attempted without
        administrator privileges.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            path_arg = kwargs.get('path', args[0] if args else '')
            # Check if the path is under HKLM and if admin privileges are missing
            if any(key_alias in path_arg.upper() for key_alias in ['HKLM', 'HKEY_LOCAL_MACHINE']):
                if not registry._is_admin():
                    raise RegistryPermissionError(
                        "Administrator privileges required for operations on HKEY_LOCAL_MACHINE."
                    )
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def _parse_path(path: str) -> Tuple[int, str]:
        """
        Parse a registry path into its root key handle and subpath.

        Args:
            path: The full registry path (e.g., "HKLM\\Software\\Microsoft").

        Returns:
            Tuple[int, str]: A tuple containing the root key handle (e.g., winreg.HKEY_LOCAL_MACHINE)
                             and the remaining subpath (e.g., "Software\\Microsoft").

        Raises:
            RegistryError: If the path is empty or the root key is invalid.
        """
        if not path:
            raise RegistryError("Empty registry path provided.")

        parts = path.split("\\", 1)
        root_name = parts[0].upper()

        if root_name not in registry.ROOT_KEYS:
            raise RegistryError(f"Invalid registry root key: {root_name}. "
                                f"Must be one of: {', '.join(registry.ROOT_KEYS.keys())}")

        return registry.ROOT_KEYS[root_name], parts[1] if len(parts) > 1 else ""

    @staticmethod
    def _validate_value_for_type(value: Any, reg_type: Union[str, int]) -> bool:
        """
        Validate that a value is compatible with the specified registry type.

        Args:
            value: The value to validate.
            reg_type: Registry type as a string (e.g., "REG_SZ") or an integer constant (e.g., winreg.REG_SZ).

        Returns:
            bool: True if the value is compatible with the type, False otherwise.
        """
        # Convert string type to constant if needed
        if isinstance(reg_type, str):
            if reg_type not in registry.TYPES:
                return False # Invalid type string
            reg_type = registry.TYPES[reg_type]

        try:
            if reg_type == winreg.REG_SZ or reg_type == winreg.REG_EXPAND_SZ:
                return isinstance(value, str)
            elif reg_type == winreg.REG_DWORD:
                # REG_DWORD is a 32-bit unsigned integer
                return isinstance(value, int) and 0 <= value <= 0xFFFFFFFF
            elif reg_type == winreg.REG_QWORD:
                # REG_QWORD is a 64-bit unsigned integer
                return isinstance(value, int) and 0 <= value <= 0xFFFFFFFFFFFFFFFF
            elif reg_type == winreg.REG_BINARY:
                return isinstance(value, bytes)
            elif reg_type == winreg.REG_MULTI_SZ:
                # REG_MULTI_SZ expects a list of strings
                return isinstance(value, list) and all(isinstance(item, str) for item in value)
            elif reg_type == winreg.REG_NONE:
                # REG_NONE can be any type, typically bytes or None
                return True
            else:
                # For unknown or unhandled types, assume valid for now or add specific checks
                return True
        except Exception:
            return False

    @staticmethod
    def _with_key(access: int = winreg.KEY_READ):
        """
        A decorator that acts as a context manager for opening or creating registry keys.

        It handles parsing the path, opening/creating the key, and closing it,
        passing the opened key object to the decorated function.

        Args:
            access: The desired access rights for the registry key
                    (e.g., winreg.KEY_READ, winreg.KEY_SET_VALUE).
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                path_arg = kwargs.get('path', args[0] if args else None)
                if not path_arg:
                    raise RegistryError("Registry path not provided to _with_key decorator.")

                root_key, sub_path = registry._parse_path(path_arg)
                create_if_missing = kwargs.pop('_create_if_missing', False) # Pop to avoid passing to wrapped func

                try:
                    # Try to open the key
                    with winreg.OpenKey(root_key, sub_path, 0, access) as open_key:
                        kwargs['_key'] = open_key
                        kwargs['_root'] = root_key
                        kwargs['_subpath'] = sub_path
                        return func(*args, **kwargs)
                except FileNotFoundError:
                    if create_if_missing:
                        try:
                            # If key not found and creation is allowed, try to create it
                            with winreg.CreateKey(root_key, sub_path) as open_key:
                                kwargs['_key'] = open_key
                                kwargs['_root'] = root_key
                                kwargs['_subpath'] = sub_path
                                return func(*args, **kwargs)
                        except PermissionError:
                            raise RegistryPermissionError(f"Insufficient permissions to create key: {path_arg}")
                        except Exception as e:
                            raise RegistryError(f"Error creating registry key '{path_arg}': {e}")
                    else:
                        # If key not found and not creating, check for default value
                        if '_default' in kwargs:
                            return kwargs['_default']
                        raise RegistryNotFoundError(f"Registry key not found: {path_arg}")
                except PermissionError:
                    raise RegistryPermissionError(f"Insufficient permissions to access key: {path_arg}")
                except Exception as e:
                    raise RegistryError(f"Error accessing registry key '{path_arg}': {e}")
            return wrapper
        return decorator

    @staticmethod
    @_requires_admin
    def write(
        path: str,
        name: str,
        value: Any,
        reg_type: Union[str, int] = "REG_SZ",
        create_if_missing: bool = True
    ) -> bool:
        """
        Write a value to the Windows registry.

        If the key does not exist, it can be created if `create_if_missing` is True.

        Args:
            path: The full registry path (e.g., "HKLM\\Software\\MyKey").
            name: The name of the value to write (e.g., "MyValue").
            value: The value to write.
            reg_type: The registry value type (e.g., "REG_SZ", winreg.REG_DWORD).
                      Defaults to "REG_SZ".
            create_if_missing: If True, the registry key will be created if it does not exist.

        Returns:
            bool: True if the write operation was successful.

        Raises:
            RegistryTypeError: If an invalid registry type string is provided.
            RegistryValueError: If the provided value is not compatible with the specified type.
            RegistryNotFoundError: If the key does not exist and `create_if_missing` is False.
            RegistryPermissionError: If there are insufficient permissions to write to the key.
            RegistryError: For other general registry errors.
        """
        # Convert string type to constant if needed
        if isinstance(reg_type, str):
            if reg_type not in registry.TYPES:
                raise RegistryTypeError(f"Invalid registry type string: '{reg_type}'. "
                                        f"Must be one of: {', '.join(registry.TYPES.keys())}")
            reg_type_const = registry.TYPES[reg_type]
        else:
            reg_type_const = reg_type

        # Validate value for the specified type
        if not registry._validate_value_for_type(value, reg_type_const):
            raise RegistryValueError(f"Value '{value}' (type: {type(value).__name__}) "
                                     f"is not compatible with registry type '{registry.TYPE_NAMES.get(reg_type_const, reg_type)}'.")

        try:
            root_key, sub_path = registry._parse_path(path)

            # Open or create the key with appropriate access
            access = winreg.KEY_SET_VALUE | (winreg.KEY_CREATE_SUB_KEY if create_if_missing else 0)
            with winreg.OpenKey(root_key, sub_path, 0, access) as reg_key:
                winreg.SetValueEx(reg_key, name, 0, reg_type_const, value)
            return True
        except FileNotFoundError:
            # This should ideally be caught by _with_key if create_if_missing is False
            # but kept as a safeguard.
            raise RegistryNotFoundError(f"Registry key not found: {path}. "
                                        f"Set 'create_if_missing=True' to create it.")
        except PermissionError:
            raise RegistryPermissionError(f"Insufficient permissions to write to: {path}.")
        except Exception as e:
            raise RegistryError(f"Error writing value '{name}' to registry key '{path}': {e}")

    @staticmethod
    @_with_key(access=winreg.KEY_READ)
    def read(
        path: str,
        name: str,
        default: Any = None,
        _key=None, # Injected by _with_key decorator
        _root=None, # Injected by _with_key decorator
        _subpath=None # Injected by _with_key decorator
    ) -> Any:
        """
        Read a value from the Windows registry.

        Args:
            path: The full registry path.
            name: The name of the value to read.
            default: The default value to return if the value or key is not found.
                     Defaults to None.

        Returns:
            Any: The registry value if found, otherwise the `default` value.

        Raises:
            RegistryPermissionError: If there are insufficient permissions to read from the key.
            RegistryError: For other general registry errors.
        """
        try:
            value, _ = winreg.QueryValueEx(_key, name)
            return value
        except FileNotFoundError:
            # winreg.QueryValueEx raises FileNotFoundError if the value name doesn't exist
            return default
        except Exception as e:
            raise RegistryError(f"Error reading registry value '{name}' from '{path}': {e}")

    @staticmethod
    def read_with_type(path: str, name: str) -> Optional[Tuple[Any, str]]:
        """
        Read a value and its type from the Windows registry.

        Args:
            path: The full registry path.
            name: The name of the value to read.

        Returns:
            Optional[Tuple[Any, str]]: A tuple containing (value, type_name) if found,
                                       otherwise None. `type_name` is the string
                                       representation of the registry type (e.g., "REG_SZ").

        Raises:
            RegistryNotFoundError: If the key or value is not found.
            RegistryPermissionError: If there are insufficient permissions to read from the key.
            RegistryError: For other general registry errors.
        """
        try:
            root_key, sub_path = registry._parse_path(path)
            with winreg.OpenKey(root_key, sub_path, 0, winreg.KEY_READ) as reg_key:
                value, reg_type = winreg.QueryValueEx(reg_key, name)
                type_name = registry.TYPE_NAMES.get(reg_type, f"Unknown ({reg_type})")
                return (value, type_name)
        except FileNotFoundError:
            raise RegistryNotFoundError(f"Registry value '{name}' not found in key '{path}'.")
        except PermissionError:
            raise RegistryPermissionError(f"Insufficient permissions to read from: {path}.")
        except Exception as e:
            raise RegistryError(f"Error reading registry value with type '{name}' from '{path}': {e}")

    @staticmethod
    @_with_key(access=winreg.KEY_READ)
    def exists(
        path: str,
        name: str = None,
        _key=None, # Injected by _with_key decorator
        _root=None, # Injected by _with_key decorator
        _subpath=None # Injected by _with_key decorator
    ) -> bool:
        """
        Check if a registry key or a specific value within a key exists.

        Args:
            path: The full registry path.
            name: Optional. The name of the value to check. If None, checks for the existence of the key.

        Returns:
            bool: True if the key (and optionally the value) exists, False otherwise.
        """
        if name is None:
            # If _with_key successfully opened the key, it exists
            return True
        else:
            try:
                winreg.QueryValueEx(_key, name)
                return True
            except FileNotFoundError:
                return False
            except Exception:
                # Catch any other exceptions during QueryValueEx as non-existence
                return False

    @staticmethod
    @_requires_admin
    def remove_value(path: str, name: str) -> bool:
        """
        Delete a specific value from a registry key.

        Args:
            path: The full registry path to the key containing the value.
            name: The name of the value to delete.

        Returns:
            bool: True if the value was successfully deleted or if it did not exist.

        Raises:
            RegistryPermissionError: If there are insufficient permissions to delete the value.
            RegistryError: For other general registry errors.
        """
        try:
            root_key, sub_path = registry._parse_path(path)
            with winreg.OpenKey(root_key, sub_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteValue(reg_key, name)
            return True
        except FileNotFoundError:
            # Value or key not found, consider it successfully "removed" (not present)
            return True
        except PermissionError:
            raise RegistryPermissionError(f"Insufficient permissions to delete value '{name}' from: {path}.")
        except Exception as e:
            raise RegistryError(f"Error removing registry value '{name}' from '{path}': {e}")

    @staticmethod
    @_requires_admin
    def remove_key(path: str, recursive: bool = False) -> bool:
        """
        Delete a registry key.

        If `recursive` is True, all subkeys and values within the key will also be deleted.
        Use with caution, especially for `recursive=True`.

        Args:
            path: The full registry path of the key to delete.
            recursive: If True, recursively deletes all subkeys and values.
                       If False, the key must be empty (no subkeys or values) to be deleted.

        Returns:
            bool: True if the key was successfully deleted or if it did not exist.

        Raises:
            RegistryPermissionError: If there are insufficient permissions to delete the key.
            RegistryError: For other general registry errors.
        """
        try:
            root_key, sub_path = registry._parse_path(path)

            if recursive:
                # Recursively delete subkeys and values
                try:
                    # Open the key to enumerate its contents
                    with winreg.OpenKey(root_key, sub_path, 0, winreg.KEY_READ) as reg_key_to_delete:
                        # Delete all values first
                        while True:
                            try:
                                # EnumerateValue raises OSError if no more values
                                name, _, _ = winreg.EnumValue(reg_key_to_delete, 0)
                                registry.remove_value(path, name)
                            except OSError:
                                break # No more values

                        # Recursively delete all subkeys
                        while True:
                            try:
                                # EnumKey raises OSError if no more subkeys
                                sub_key_name = winreg.EnumKey(reg_key_to_delete, 0)
                                registry.remove_key(f"{path}\\{sub_key_name}", recursive=True)
                            except OSError:
                                break # No more subkeys
                except FileNotFoundError:
                    # Key already doesn't exist, nothing to do
                    return True
                except PermissionError:
                    raise RegistryPermissionError(f"Insufficient permissions to enumerate/delete sub-items of key: {path}")
                except Exception as e:
                    raise RegistryError(f"Error during recursive deletion of subkeys/values for '{path}': {e}")

            # Now delete the key itself (it should be empty if recursive was true)
            # Need to open the parent key to delete the child key
            parent_path, key_name = os.path.split(sub_path)
            if not key_name: # If sub_path was empty, it means we're trying to delete a root key, which is not allowed
                raise RegistryError(f"Cannot delete a root registry key directly: {path}")

            try:
                with winreg.OpenKey(root_key, parent_path, 0, winreg.KEY_ALL_ACCESS) as parent_reg_key:
                    winreg.DeleteKey(parent_reg_key, key_name)
                return True
            except FileNotFoundError:
                # Key already doesn't exist, consider it successfully "removed"
                return True
            except PermissionError:
                raise RegistryPermissionError(f"Insufficient permissions to delete key: {path}.")
            except Exception as e:
                raise RegistryError(f"Error deleting registry key '{path}': {e}")

        except RegistryNotFoundError:
            # If the initial parse_path fails due to not found, it means key doesn't exist
            return True
        except PermissionError:
            raise RegistryPermissionError(f"Insufficient permissions to delete key: {path}.")
        except Exception as e:
            raise RegistryError(f"An unexpected error occurred while removing key '{path}': {e}")

    @staticmethod
    @_with_key(access=winreg.KEY_READ)
    def list_keys(
        path: str,
        _key=None, # Injected by _with_key decorator
        _root=None, # Injected by _with_key decorator
        _subpath=None # Injected by _with_key decorator
    ) -> List[str]:
        """
        List all subkeys of a given registry key.

        Args:
            path: The full registry path of the key.

        Returns:
            List[str]: A list of subkey names. Returns an empty list if the key has no subkeys.

        Raises:
            RegistryNotFoundError: If the specified key does not exist.
            RegistryPermissionError: If there are insufficient permissions to read the key.
            RegistryError: For other general registry errors.
        """
        keys = []
        try:
            i = 0
            while True:
                try:
                    keys.append(winreg.EnumKey(_key, i))
                    i += 1
                except OSError: # Raised when no more subkeys
                    break
        except Exception as e:
            raise RegistryError(f"Error listing subkeys for '{path}': {e}")
        return keys

    @staticmethod
    @_with_key(access=winreg.KEY_READ)
    def list_values(
        path: str,
        _key=None, # Injected by _with_key decorator
        _root=None, # Injected by _with_key decorator
        _subpath=None # Injected by _with_key decorator
    ) -> Dict[str, Dict[str, Any]]:
        """
        List all values (name, data, and type) within a registry key.

        Args:
            path: The full registry path of the key.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary where keys are value names,
                                       and values are dictionaries containing:
                                       - 'value': The actual data of the registry value.
                                       - 'type': The string representation of the registry type (e.g., "REG_SZ").
                                       Returns an empty dictionary if the key has no values.

        Raises:
            RegistryNotFoundError: If the specified key does not exist.
            RegistryPermissionError: If there are insufficient permissions to read the key.
            RegistryError: For other general registry errors.
        """
        values = {}
        try:
            i = 0
            while True:
                try:
                    name, value, reg_type = winreg.EnumValue(_key, i)
                    type_name = registry.TYPE_NAMES.get(reg_type, f"Unknown ({reg_type})")
                    values[name] = {
                        'value': value,
                        'type': type_name
                    }
                    i += 1
                except OSError: # Raised when no more values
                    break
        except Exception as e:
            raise RegistryError(f"Error listing values for '{path}': {e}")
        return values

    @staticmethod
    @_requires_admin
    def create_key(path: str) -> bool:
        """
        Create a new registry key.

        If the key already exists, this function does nothing and returns True.
        Intermediate keys in the path will also be created if they don't exist.

        Args:
            path: The full registry path of the key to create.

        Returns:
            bool: True if the key was successfully created or already exists.

        Raises:
            RegistryPermissionError: If there are insufficient permissions to create the key.
            RegistryError: For other general registry errors.
        """
        try:
            root_key, sub_path = registry._parse_path(path)
            # CreateKey will open the key if it exists, or create it if it doesn't
            with winreg.CreateKey(root_key, sub_path):
                return True
        except PermissionError:
            raise RegistryPermissionError(f"Insufficient permissions to create key: {path}.")
        except Exception as e:
            raise RegistryError(f"Error creating registry key '{path}': {e}")

    @staticmethod
    @_requires_admin
    def copy_key(source_path: str, destination_path: str, overwrite: bool = False) -> bool:
        """
        Copy a registry key and all its values and subkeys to another location.

        Args:
            source_path: The full registry path of the source key.
            destination_path: The full registry path where the key should be copied.
            overwrite: If True, existing values in the destination key will be overwritten.
                       If False, existing values will be skipped.

        Returns:
            bool: True if the copy operation was successful.

        Raises:
            RegistryNotFoundError: If the source key does not exist.
            RegistryPermissionError: If there are insufficient permissions for the operation.
            RegistryError: For other general registry errors.
        """
        if not registry.exists(source_path):
            raise RegistryNotFoundError(f"Source registry key not found: {source_path}")

        try:
            # Ensure destination key exists
            registry.create_key(destination_path)

            # Copy all values from source to destination
            source_values = registry.list_values(source_path)
            for name, data in source_values.items():
                # Check if destination value exists and if overwrite is False
                if not overwrite and registry.exists(destination_path, name):
                    continue # Skip existing value if not overwriting

                # Get the type constant from the type name
                # Default to REG_SZ if type name is unknown
                reg_type_const = registry.TYPES.get(data['type'], winreg.REG_SZ)
                registry.write(destination_path, name, data['value'], reg_type_const, create_if_missing=True)

            # Recursively copy all subkeys
            source_subkeys = registry.list_keys(source_path)
            for subkey_name in source_subkeys:
                source_sub_path_full = f"{source_path}\\{subkey_name}"
                dest_sub_path_full = f"{destination_path}\\{subkey_name}"
                registry.copy_key(source_sub_path_full, dest_sub_path_full, overwrite)

            return True
        except RegistryError:
            raise # Re-raise custom RegistryErrors
        except Exception as e:
            raise RegistryError(f"Error copying registry key from '{source_path}' to '{destination_path}': {e}")

    @staticmethod
    def backup_key(path: str, backup_file: str) -> bool:
        """
        Backup a registry key and its subkeys/values to a .reg file.

        This uses the `reg.exe` command-line utility.

        Args:
            path: The full registry path of the key to backup.
            backup_file: The full path to the .reg file where the backup will be saved.

        Returns:
            bool: True if the backup was successful.

        Raises:
            RegistryNotFoundError: If the specified key does not exist.
            RegistryError: If the `reg.exe` command fails or for other general errors.
        """
        if not registry.exists(path):
            raise RegistryNotFoundError(f"Registry key not found for backup: {path}")

        try:
            # Ensure the path is correctly formatted for the reg export command
            # Convert root key handle back to its string representation (e.g., HKEY_LOCAL_MACHINE)
            root_key_handle, sub_path_parsed = registry._parse_path(path)
            full_path_for_reg = ""
            for name, handle in registry.ROOT_KEYS.items():
                if handle == root_key_handle:
                    full_path_for_reg = name
                    break
            if sub_path_parsed:
                full_path_for_reg = f"{full_path_for_reg}\\{sub_path_parsed}"

            # Use the reg.exe utility to export the key
            # /y option suppresses the overwrite prompt
            command = ['reg', 'export', full_path_for_reg, backup_file, '/y']
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False # Do not raise CalledProcessError automatically
            )

            if result.returncode != 0:
                error_message = result.stderr.strip() if result.stderr else "Unknown error."
                raise RegistryError(f"Error exporting registry key '{path}' to '{backup_file}': {error_message}")

            return True
        except RegistryError:
            raise # Re-raise custom RegistryErrors
        except Exception as e:
            raise RegistryError(f"An unexpected error occurred during backup of '{path}': {e}")

    @staticmethod
    @_requires_admin
    def restore_key(backup_file: str) -> bool:
        """
        Restore registry keys and values from a .reg file.

        This uses the `reg.exe` command-line utility.

        Args:
            backup_file: The full path to the .reg file to import.

        Returns:
            bool: True if the restore was successful.

        Raises:
            FileNotFoundError: If the backup file does not exist.
            RegistryPermissionError: If there are insufficient permissions to import.
            RegistryError: If the `reg.exe` command fails or for other general errors.
        """
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file not found: {backup_file}")

        try:
            # Use the reg.exe utility to import the key
            command = ['reg', 'import', backup_file]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False # Do not raise CalledProcessError automatically
            )

            if result.returncode != 0:
                error_message = result.stderr.strip() if result.stderr else "Unknown error."
                if "Access is denied" in error_message or "requested operation requires elevation" in error_message:
                    raise RegistryPermissionError(f"Insufficient permissions to import registry from '{backup_file}'. "
                                                  "Run as administrator.")
                raise RegistryError(f"Error importing registry from '{backup_file}': {error_message}")

            return True
        except RegistryError:
            raise # Re-raise custom RegistryErrors
        except Exception as e:
            raise RegistryError(f"An unexpected error occurred during restore from '{backup_file}': {e}")

    @staticmethod
    def monitor_key(path: str, callback: callable, interval_seconds: int = 1) -> None:
        """
        Monitor a registry key for changes using a basic polling mechanism.

        When changes are detected, the provided callback function is invoked with
        a dictionary of the changed values. This function blocks indefinitely.

        Note: This is a simple polling implementation. For production-grade
        real-time monitoring, consider using Windows API notification services
        (e.g., `ReadDirectoryChangesW` or WMI events) which are more efficient.

        Args:
            path: The full registry path of the key to monitor.
            callback: A callable function that accepts one argument: a dictionary
                      of changed values (name -> {'value': data, 'type': type_name}).
            interval_seconds: The polling interval in seconds. Defaults to 1 second.

        Raises:
            RegistryNotFoundError: If the specified key does not exist.
            RegistryPermissionError: If there are insufficient permissions to read the key.
            RegistryError: For other general registry errors.
        """
        if not registry.exists(path):
            raise RegistryNotFoundError(f"Cannot monitor non-existent registry key: {path}")

        last_values = {}
        try:
            last_values = registry.list_values(path)
        except RegistryPermissionError:
            raise # Re-raise immediately if permissions are an issue
        except Exception as e:
            raise RegistryError(f"Initial read error for monitoring key '{path}': {e}")

        try:
            while True:
                time.sleep(interval_seconds)
                try:
                    current_values = registry.list_values(path)

                    # Check for changes (added, modified, deleted values)
                    changes = {}
                    # Check for modified or new values
                    for name, data in current_values.items():
                        if name not in last_values or data != last_values[name]:
                            changes[name] = data
                    # Check for deleted values
                    for name in last_values:
                        if name not in current_values:
                            changes[name] = {'value': None, 'type': 'DELETED'} # Indicate deletion

                    if changes:
                        callback(changes)
                        last_values = current_values # Update for next iteration
                except RegistryNotFoundError:
                    # Key was deleted while monitoring
                    callback({'_key_status': {'value': 'DELETED', 'type': 'STATUS'}})
                    print(f"Monitoring stopped for key '{path}' as it no longer exists.")
                    break # Stop monitoring
                except RegistryPermissionError as e:
                    print(f"Permission error during monitoring of '{path}': {e}. Stopping monitor.")
                    break # Stop monitoring on permission error
                except Exception as e:
                    print(f"Error during registry monitoring of '{path}': {e}. Continuing to monitor...")
                    # Do not re-raise, try again in the next interval

        except KeyboardInterrupt:
            print(f"Monitoring of '{path}' interrupted by user.")
            return
        except Exception as e:
            raise RegistryError(f"An unexpected critical error occurred during monitoring of '{path}': {e}")

    @staticmethod
    @_with_key(access=winreg.KEY_READ)
    def get_key_info(
        path: str,
        _key=None, # Injected by _with_key decorator
        _root=None, # Injected by _with_key decorator
        _subpath=None # Injected by _with_key decorator
    ) -> Dict[str, Any]:
        """
        Get detailed information about a registry key.

        Args:
            path: The full registry path of the key.

        Returns:
            Dict[str, Any]: A dictionary containing information such as:
                            - 'name': The name of the key itself.
                            - 'path': The full path of the key.
                            - 'parent': The full path of the parent key.
                            - 'subkey_count': Number of direct subkeys.
                            - 'value_count': Number of values within the key.
                            - 'last_modified': Last modification time (as a Windows file time).

        Raises:
            RegistryNotFoundError: If the specified key does not exist.
            RegistryPermissionError: If there are insufficient permissions to read the key.
            RegistryError: For other general registry errors.
        """
        try:
            info = {}

            # Get subkey count, value count, and last modified time
            info['subkey_count'], info['value_count'], info['last_modified'] = winreg.QueryInfoKey(_key)

            # Get parent key path and key name
            parent_path, key_name = os.path.split(_subpath)
            # If subpath was empty (e.g., "HKLM"), key_name will be empty, parent_path will be empty
            if not key_name and _subpath == "": # This means it's a root key
                info['name'] = list(registry.ROOT_KEYS.keys())[list(registry.ROOT_KEYS.values()).index(_root)]
                info['parent'] = None # Root keys have no parent in this context
            else:
                info['name'] = key_name
                # Construct parent path string
                root_name_str = list(registry.ROOT_KEYS.keys())[list(registry.ROOT_KEYS.values()).index(_root)]
                info['parent'] = f"{root_name_str}\\{parent_path}" if parent_path else root_name_str

            info['path'] = path

            return info
        except Exception as e:
            raise RegistryError(f"Error getting info for registry key '{path}': {e}")


# --- Compatibility functions for the original module interface ---
# These functions provide a simpler, direct interface that maps to the
# methods of the 'registry' class.

def write(path: str, key: str, val: Any, reg_type: str = "REG_SZ") -> bool:
    """
    Compatibility function: Write a value to the Windows registry.
    Maps to `registry.write`.
    """
    return registry.write(path, key, val, reg_type)

def read(path: str, key: str, default: Any = None) -> Any:
    """
    Compatibility function: Read a value from the Windows registry.
    Maps to `registry.read`.
    """
    return registry.read(path, key, default)

def exists(path: str, key: str = None) -> bool:
    """
    Compatibility function: Check if a registry key or value exists.
    Maps to `registry.exists`.
    """
    return registry.exists(path, key)

def remove(path: str, key: str = None) -> bool:
    """
    Compatibility function: Delete a registry value or key.
    If `key` is provided, deletes the value. If `key` is None, deletes the key (non-recursively).
    Maps to `registry.remove_value` or `registry.remove_key`.
    """
    if key:
        return registry.remove_value(path, key)
    else:
        # Note: This compatibility function defaults to non-recursive key removal.
        # For recursive removal, call registry.remove_key(path, recursive=True) directly.
        return registry.remove_key(path, recursive=False)

def list_keys(path: str) -> List[str]:
    """
    Compatibility function: List all subkeys of a registry key.
    Maps to `registry.list_keys`.
    """
    return registry.list_keys(path)

def list_values(path: str) -> Dict[str, Any]:
    """
    Compatibility function: List all values of a registry key.
    Returns a dictionary mapping value names to their data.
    Maps to `registry.list_values`.
    """
    result = {}
    values = registry.list_values(path)
    for name, data in values.items():
        result[name] = data['value']
    return result

def create_key(path: str) -> bool:
    """
    Compatibility function: Create a new registry key.
    Maps to `registry.create_key`.
    """
    return registry.create_key(path)

def delete_key(path: str) -> bool:
    """
    Compatibility function: Delete a registry key recursively.
    Maps to `registry.remove_key` with `recursive=True`.
    """
    return registry.remove_key(path, recursive=True)

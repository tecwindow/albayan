import shutil
import sys
import os
from cx_Freeze import setup, Executable
import PyQt6

def rename_main_file(to_name="Albayan.py"):
    if os.path.exists("main.py"):
        os.rename("main.py", to_name)
    return to_name

def restore_main_file(from_name="Albayan.py"):
    if os.path.exists(from_name):
        os.rename(from_name, "main.py")

def get_pyqt_dll_files():
    pyqt_path = os.path.dirname(PyQt6.__file__)
    dll_files = ["Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll", "Qt6Network.dll"]
    return [(os.path.join(pyqt_path, "Qt6", "bin", file), os.path.join("lib", file)) for file in dll_files]

def get_include_files():
    base_files = [
        ("database", "database"),
        ("documentation", "documentation"),
        ("Audio", "Audio"),
        ("bass.dll", "bass.dll"),
        ("Albayan.ico", "Albayan.ico")
    ]
    base_files.extend(get_pyqt_dll_files())
    return base_files

def build_setup(script_name="Albayan.py", build_dir="albayan_build", version="4.0.1"):
    include_files = get_include_files()
    build_exe_options = {
        "build_exe": build_dir,
        "optimize": 1,
        "include_files": include_files,
        "packages": ["core_functions", "theme", "ui", "utils"],
        "includes": [
            "PyQt6.QtCore", "PyQt6.QtWidgets", "PyQt6.QtGui", "PyQt6.QtMultimedia",
            "packaging", "requests", "UniversalSpeech", "sqlalchemy",
            "sqlalchemy.dialects.sqlite", "apscheduler"
        ],
        "excludes": ["tkinter", "test", "setuptools", "pip", "numpy", "unittest"],
        "include_msvcr": True
    }

    setup(
        name="Albayan",
        version=version,
        description="Albayan",
        long_description="البيان - Albayan, كل ما يخص الإسلام",
        author="TecWindow",
        author_email="support@tecwindow.net",
        url="https://tecwindow.net",
        download_url="https://github.com/tecwindow/albayan",
        keywords=["islamic", "islam", "quran", "desktop", "alquran", "tecwindow", "القرآن", "إسلام"],
        options={"build_exe": build_exe_options},
        executables=[
            Executable(
                script_name,
                base="Win32GUI" if sys.platform == "win32" else None,
                target_name="Albayan.exe",
                icon="Albayan.ico",
                copyright="2025 tecwindow"
            )
        ]
    )

def clean_unused_folders(build_dir="albayan_build"):
    folder_paths = [
        os.path.join(build_dir, "lib/PyQt6/Qt6/bin"),
        os.path.join(build_dir, "lib/PyQt6/Qt6/translations"),
        os.path.join(build_dir, "lib/PyQt6/Qt6/plugins/multimedia")
    ]
    for folder in folder_paths:
        try:
            shutil.rmtree(os.path.abspath(folder))
        except Exception as e:
            print(f"Error removing {folder}: {e}")

def main():
    build_dir = os.environ.get("ALBAYAN_BUILD_DIR", "albayan_build")
    version = os.environ.get("ALBAYAN_VERSION", "4.0.1")

    script_name = rename_main_file()
    try:
        build_setup(script_name, build_dir=build_dir, version=version)
        clean_unused_folders(build_dir)
    finally:
        restore_main_file(script_name)

if __name__ == "__main__":
    main()

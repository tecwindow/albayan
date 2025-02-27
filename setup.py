import shutil
import sys
import os
from cx_Freeze import setup, Executable
import PyQt6

pyqt_path = os.path.dirname(PyQt6.__file__)

if os.path.exists("main.py"):
    os.rename("main.py", "Albayan.py")

include_files = [
    ("database", "database"),
    ("documentation", "documentation"),
    ("Audio", "Audio"),
    ("bass.dll", "bass.dll"),
    ("Albayan.ico", "Albayan.ico")
]
dll_files = ["Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll", "Qt6Network.dll"]
for file in dll_files:
    include_files.append((os.path.join(pyqt_path, "Qt6", "bin", file), os.path.join("lib", file)))


build_exe_options = {
    "build_exe": "albayan_build",
    "optimize": 1,
    "include_files": include_files,
    "packages": ["core_functions", "theme", "ui", "utils"],
    "includes": ["PyQt6.QtCore", "PyQt6.QtWidgets", "PyQt6.QtGui", "PyQt6.QtMultimedia", "packaging", "requests", "UniversalSpeech", "sqlalchemy", "sqlalchemy.dialects.sqlite", "apscheduler"],
    "excludes": ["tkinter", "test", "setuptools", "pip", "numpy", "unittest"],
    "include_msvcr": True
}

setup(
    name="Albayan",
    version="3.0.0",
    description="Albayan",
    long_description="البيان - Albayan, كل ما يخص الإسلام",
    author="TecWindow",
    author_email="support@tecwindow.net",
    url="https://tecwindow.net/en",
    download_url="https://github.com/tecwindow/albayan",
    keywords=["islamic", "islam", "quran", "desktop", "alquran", "tecwindow", "القرآن", "إسلام"],
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "Albayan.py",
            base="Win32GUI" if sys.platform == "win32" else None,
            target_name="Albayan.exe",
            icon="Albayan.ico",
            copyright="2025 tecwindow"
        )
    ]
)

folder_paths = ["albayan_build/lib/PyQt6/Qt6/bin", "albayan_build/lib/PyQt6/Qt6/translations"]
for folder in folder_paths:
    try:
        shutil.rmtree(os.path.abspath(folder))
    except Exception as e:
        print(f"Error removing {folder}: {e}")

if os.path.exists("Albayan.py"):
    os.rename("Albayan.py", "main.py")

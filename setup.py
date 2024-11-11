import shutil
import sys
import os
from cx_Freeze import setup, Executable

import PyQt6
pyqt_path = os.path.dirname(PyQt6.__file__)

# Include additional files and DLLs
include_files = [("database", "database"), ("Audio", "Audio"), ("bass.dll", "bass.dll"), ("icon.webp", "icon.webp")]
dll_files = ["Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll", "Qt6Network.dll"]
for file in dll_files:
    include_files.append((os.path.join(pyqt_path, "Qt6", "bin", file), os.path.join("lib", file)))

build_exe_options = {
    "build_exe": "albayan_build",
    "optimize": 1,
    "include_files": include_files,
    "packages": ["core_functions", "theme", "ui", "utils"],
    "includes": ["PyQt6.QtCore", "PyQt6.QtWidgets", "PyQt6.QtGui", "PyQt6.QtMultimedia", "packaging", "requests", "UniversalSpeech", "sqlalchemy", "sqlalchemy.dialects.sqlite", "apscheduler"],
    "excludes": ["tkinter", "test", "setuptools", "pip", "numpy"],
    "include_msvcr": True
}

description = "albayan"
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="albayan",
    version="1.2.3",
    description=description,
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)

#clean
folder_paths = ["albayan_build/lib/PyQt6/Qt6/bin", "albayan_build/lib/PyQt6/Qt6/translations"]
for folder in folder_paths:
    try:
        shutil.rmtree(os.path.abspath(folder))
    except:
        pass

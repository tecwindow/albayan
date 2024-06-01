import sys
import os
from cx_Freeze import setup, Executable

import PyQt6
pyqt_path = os.path.dirname(PyQt6.__file__)


build_exe_options = {
    "build_exe": "albayan_build",
    "optimize": 1,
    "include_files": [
        ("database", "database"), 
        ("sounds", "sounds"),
        (os.path.join(pyqt_path, "Qt6", "bin"), "Qt6/bin")
    ],
    "packages": ["core_functions", "theme", "ui", "utils"],
    "includes": ["PyQt6.QtCore", "PyQt6.QtWidgets", "PyQt6.QtGui", "packaging", "requests", "UniversalSpeech"],
    "excludes": ["tkinter", "test", "setuptools", "pip", "numpy"],
    "include_msvcr": True
}

description = "albayan"
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="albayan",
    version="1.0.0",
    description=description,
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)

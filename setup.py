import shutil
import sys
import os
from cx_Freeze import setup, Executable
import PySide6


def rename_main_file(to_name="Albayan.py"):
    if os.path.exists("main.py"):
        os.rename("main.py", to_name)
    return to_name


def restore_main_file(from_name="Albayan.py"):
    if os.path.exists(from_name):
        os.rename(from_name, "main.py")


def get_pyside_dll_files():
    pyside_path = os.path.dirname(PySide6.__file__)
    dll_files = ["Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll", "Qt6Network.dll"]
    return [
        (os.path.join(pyside_path, file), os.path.join("lib", file))
        for file in dll_files
    ]


def get_include_files():
    base_files = [
        ("database", "database"),
        ("documentation", "documentation"),
        ("Audio", "Audio"),
        ("bass.dll", "bass.dll"),
        ("Albayan.ico", "Albayan.ico"),
    ]
    base_files.extend(get_pyside_dll_files())
    return base_files


def build_setup(script_name="Albayan.py", build_dir="albayan_build", version="6.2.1"):
    include_files = get_include_files()
    build_exe_options = {
        "build_exe": build_dir,
        "optimize": 2,
        "include_files": include_files,
        "packages": ["core_functions", "theme", "ui", "utils"],
        "includes": [
            "PySide6.QtCore",
            "PySide6.QtWidgets",
            "PySide6.QtGui",
            "PySide6.QtNetwork",
            "packaging",
            "requests",
            "UniversalSpeech",
            "sqlalchemy",
            "sqlalchemy.dialects.sqlite",
            "apscheduler",
        ],
        "excludes": [
            "tkinter",
            "test",
            "unittest",
            "setuptools",
            "pip",
            "numpy",
            "pydantic",
            "pydantic_core",
            "annotated_types",
            "typing_inspection",
            "striprtf",
            "PySide6.QtMultimedia",
            "PySide6.Qt3DCore",
            "PySide6.Qt3DAnimation",
            "PySide6.Qt3DExtras",
            "PySide6.Qt3DInput",
            "PySide6.Qt3DLogic",
            "PySide6.Qt3DQuick",
            "PySide6.QtBluetooth",
            "PySide6.QtCharts",
            "PySide6.QtDataVisualization",
            "PySide6.QtDesigner",
            "PySide6.QtGraphs",
            "PySide6.QtHelp",
            "PySide6.QtHttpServer",
            "PySide6.QtLocation",
            "PySide6.QtLottie",
            "PySide6.QtNfc",
            "PySide6.QtPdf",
            "PySide6.QtPositioning",
            "PySide6.QtQuick",
            "PySide6.QtQuick3D",
            "PySide6.QtQuickControls2",
            "PySide6.QtQuickWidgets",
            "PySide6.QtRemoteObjects",
            "PySide6.QtScxml",
            "PySide6.QtSensors",
            "PySide6.QtSerialBus",
            "PySide6.QtSerialPort",
            "PySide6.QtSpatialAudio",
            "PySide6.QtStateMachine",
            "PySide6.QtTextToSpeech",
            "PySide6.QtVirtualKeyboard",
            "PySide6.QtWebChannel",
            "PySide6.QtWebEngineCore",
            "PySide6.QtWebSockets",
            "PySide6.QtWebView",
            "pydoc",
            "pydoc_data",
            "xmlrpc",
            "curses",
            "_pyrepl",
        ],
        "include_msvcr": False,
        "replace_paths": ["*="],
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
        keywords=[
            "islamic",
            "islam",
            "quran",
            "desktop",
            "alquran",
            "tecwindow",
            "القرآن",
            "إسلام",
        ],
        options={"build_exe": build_exe_options},
        executables=[
            Executable(
                script_name,
                base="gui",
                target_name="Albayan.exe",
                icon="Albayan.ico",
                copyright="2026 tecwindow",
            )
        ],
    )


def clean_unused_folders(build_dir="albayan_build"):
    folders_to_remove = [
        "lib/PySide6/translations",
        "lib/PySide6/qml",
        "lib/PySide6/resources",
        "lib/PySide6/plugins/multimedia",
        "lib/PySide6/plugins/designer",
        "lib/PySide6/plugins/qmltooling",
        "lib/PySide6/plugins/qmllint",
        "lib/PySide6/plugins/sceneparsers",
        "lib/PySide6/plugins/assetimporters",
        "lib/PySide6/plugins/renderers",
        "lib/PySide6/plugins/canbus",
        "lib/PySide6/plugins/geoservices",
        "lib/PySide6/plugins/sensors",
        "lib/PySide6/plugins/texttospeech",
        "lib/PySide6/plugins/webview",
        "lib/PySide6/plugins/position",
        "lib/PySide6/plugins/geometryloaders",
    ]
    for rel_path in folders_to_remove:
        full_path = os.path.join(build_dir, rel_path)
        if os.path.exists(full_path):
            try:
                shutil.rmtree(full_path)
                print(f"Removed unused folder: {rel_path}")
            except Exception as e:
                print(f"Error removing {full_path}: {e}")

    # Remove unneeded multimedia and FFmpeg DLLs if bundled by any dependency
    unused_dll_prefixes = [
        "avcodec",
        "avformat",
        "avutil",
        "swresample",
        "swscale",
        "Qt6Multimedia",
        "Qt6SpatialAudio",
    ]
    lib_dir = os.path.join(build_dir, "lib")
    if os.path.exists(lib_dir):
        for root, _, files in os.walk(lib_dir):
            for file in files:
                if any(file.startswith(prefix) and file.endswith(".dll") for prefix in unused_dll_prefixes):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"Removed unused DLL: {file}")
                    except Exception as e:
                        print(f"Error removing {file_path}: {e}")


def main():
    build_dir = os.environ.get("ALBAYAN_BUILD_DIR", "albayan_build")
    version = os.environ.get("ALBAYAN_VERSION", "6.2.1")

    script_name = rename_main_file()
    try:
        build_setup(script_name, build_dir=build_dir, version=version)
        clean_unused_folders(build_dir)
    finally:
        restore_main_file(script_name)


if __name__ == "__main__":
    main()

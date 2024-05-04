import os

tecwindow_folder = os.path.join(os.getenv("AppData"), "tecwindow")
albayan_folder = os.path.join(tecwindow_folder, "albayan")
os.makedirs(albayan_folder, exist_ok=True)

# program information
program_name = "البيان"
program_version = "1.0"

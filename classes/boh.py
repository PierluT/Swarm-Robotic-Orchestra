import os
from pathlib import Path

current_path =  Path(__file__).parent
simulation_number = 10
name = "csv"

for i in range(simulation_number):
    new_directory_name = f"{name}_{i}"

    # Create the directory
    try:
        os.mkdir(new_directory_name)
        print(f"Directory '{new_directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{new_directory_name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{new_directory_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
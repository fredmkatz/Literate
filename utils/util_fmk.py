import os
import shutil
from typing import Dict, Any

import datetime
import glob
import inspect
import yaml

from utils.util_flogging import flogger


def write_text(file, text):
    """
    Writes a whole text file (UTF-8 encoded).
    """
    with open(file, mode="w", encoding="utf-8") as f:
        f.write(text)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        data = file.read()
    return data


def read_lines(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        data = file.read()
    return data.split("\n")


def glob_files(*file_list):
    """Processes a list of files using glob."""
    all_matching_files = []
    for pattern in file_list:
        print(f"pattern is {pattern}")
        matching_files = glob.glob(pattern)
        all_matching_files.extend(matching_files)
    return all_matching_files


def is_stale(target, *sources):
    #    print(f"Is {target} stale?...")
    if not os.path.exists(target):
        #      print("\tYES. Doesn't exist")
        return True
    for source in sources:
        if is_newer(source, target):
            #         print(f"\tYES: Source: {source} newer than\n\tstale target: {target}")
            return True
    #  print(f"\tNO: newer than {sources}")
    return False


def is_newer(file1, file2):
    """
    Checks if file1 is newer than file2.
    Returns True if file1 is newer or if file2 doesn't exist, False otherwise.
    """
    if not os.path.exists(file2):
        return True

    return os.path.getmtime(file1) > os.path.getmtime(file2)


def show_times(*files):
    for file in files:
        timestamp = os.path.getmtime(file)

        # Convert timestamp to datetime object
        datetime_object = datetime.datetime.fromtimestamp(timestamp)

        # Format the datetime object
        formatted_time = datetime_object.strftime("%Y-%m-%d %H:%M:%S")  # Example format

        print(f"{formatted_time}\t{file}")
    return


def debug():
    pass



def create_fresh_directory(dir_path):
    """Creates a fresh directory at the given path.
    Removes the directory first if it exists.
    """
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(
                dir_path, ignore_errors=True
            )  # Remove existing directory and its contents
            print(f"Directory '{dir_path}' and its contents have been removed.")
        except FileNotFoundError:
            print(f"Directory '{dir_path}' not found.")
        except PermissionError:
            print(f"Permission denied: Unable to remove '{dir_path}'.")
        except OSError as e:
            print(f"Error removing '{dir_path}': {e}")

    os.makedirs(dir_path)  # Create the directory (and any necessary parent directories)

def remove_directory_if_exists(dir_path):
    """Removes a directory and its contents if it exists.

    Args:
      dir_path: The path to the directory to remove.
    """
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
            print(f"Directory '{dir_path}' removed successfully.")
        except OSError as e:
            print(f"Error removing directory '{dir_path}': {e}")
    else:
        print(f"Directory '{dir_path}' does not exist.")


def get_caller_name():
    """Returns the name of the calling function."""
    stack = inspect.stack()
    if len(stack) < 3:
        return None  # No caller function
    caller_frame = stack[2]  # Index 0 is current, 1 is this function, 2 is the caller
    return caller_frame.function

import sys
import traceback
def tell_me(message):
    print("\n", file=sys.stderr)
    print("\n", file=sys.stdout)
    print(message, file=sys.stderr)
    print(message, file=sys.stdout)
    traceback.print_stack(file=sys.stdout)
    traceback.print_stack(file=sys.stderr)


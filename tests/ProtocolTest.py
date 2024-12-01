import sys
import os

# Add the project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from inc.Utility.Utility import Utility
from inc.Model.Request import Request


def mock_ls(utility: Utility, directory_path: str):
    # Create a Request object with the specified directory path
    request = Request(cmd="ls", local_path=directory_path)

    # Call the ls method of the Utility class
    response = utility.ls(request)

    # Check the response status and print the results
    if response.status == "success" and response.code == None:
        print(f"Listing for directory: {directory_path or utility.local_working_directory}\n")
        for entry in response.contents:
            entry_type = "Directory" if entry.type == "dir" else "File"
            print(f"{entry_type:10} | {entry.name:30} | {entry.size:10} bytes")
    else:
        print(f"Error: {response.message}")

def mock_cd(utility: Utility, directory_path: str):
    # Create a Request object with the specified directory path
    request = Request(cmd="cd", local_path=directory_path)

    print(f"Requested Path: {request.local_path}")
    # Call the ls method of the Utility class
    response = utility.cd(request)

    # Check the response status and print the results
    if response.status == "success" and response.code == None:
        print(f"{response.message or utility.local_working_directory}\n")
    else:
        print(f"Error: {response.message}")

def mock_mkdir(utility: Utility, directory_path: str):
    # Create a Request object with the specified directory path
    request = Request(cmd="mkdir", local_path=directory_path)

    # Call the ls method of the Utility class
    response = utility.mkdir(request)

    # Check the response status and print the results
    if response.status == "success" and response.code == None:
        print(f"{response.message}\n")
    else:
        print(f"Error: {response.message}")

if __name__ == "__main__":

    util = Utility()

    mock_ls(util, util.local_working_directory)
    mock_mkdir(util, "test")
    mock_ls(util, util.local_working_directory)
    mock_cd(util, "test")
    mock_ls(util, util.local_working_directory)

    
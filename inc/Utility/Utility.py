# Trey Rubino 

# Common functionality.

import os
import stat
import grp
import pwd
from typing import Type
from datetime import datetime

from ..Model.Request import Request
from ..Model.Response import Response, Content
from ..Model.CustomProtocol import CustomProtocol
from .sec_check import normalize_path

# Utility
# Contains helper functions for both Server and Client to use.
# Handles all commands as well as send and receive.
# All command returns will be type `Response`,
# and the `recv_all` return is dynamic. The use can specify 
# which object they want built and returned to them (either Request or Response).
# Please see `Response.py` and `Request.py` model classes for their set of properties to work with.
class Utility:

    # constructor
    # Sets the current working directory
    def __init__(self):
        self.local_working_directory = os.getcwd()
        
    def help(self, request: Request) -> Response:
        try:
            help_commands = {
                # Remote Commands
                "exit": "Quit the application.",
                "help": "[command] Display this help text.",
                "cd": "Change remote directory to 'path'. If 'path' is not specified, change to the session's starting directory.",
                "ls": "[-l] Display a remote directory listing of 'path' or the current directory if 'path' is not specified. Use the '-l' flag for detailed listing.",
                "mkdir": "[-r] Create a remote directory specified by 'path'.",
                "pwd": "Display the remote working directory.",
                "get": (
                    "[-r] Retrieve 'remote-path' and store it on the local machine. If 'local-path' is not specified, use the same name as on the remote machine. "
                    "If the '-r' flag is specified, directories are copied recursively."
                ),
                "put": (
                    "[-r] Upload 'local-path' and store it on the remote machine. If 'remote-path' is not specified, use the same name as on the local machine. "
                    "If the '-r' flag is specified, directories are copied recursively."
                ),
                # Local Commands
                "lcd": "Change local directory to 'path'. If 'path' is not specified, change to the user's home directory.",
                "lls": "[-l] Display local directory listing of 'path' or the current directory if 'path' is not specified.",
                "lmkdir": "[-r] Create a local directory specified by 'path'.",
                "lpwd": "Print the local working directory."
            }

            if not request.remote_path:  # If no specific command is requested
                all_help_text = "\n".join([f"{cmd}: {desc}" for cmd, desc in help_commands.items()])
                return Response(status="success", message=all_help_text)
            else:  # If a specific command is requested
                help_text = help_commands.get(request.remote_path)
                if help_text:
                    return Response(status="success", message=help_text)
                else:
                    return Response(status="error", message=f"Unknown command '{request.remote_path}'.", code="ERR_HELP_UNKNOWN")
        except Exception as e:
            return Response(status="error", message=f"Failed to generate help text: {str(e)}", code="ERR_HELP")

    # clear
    # Clears the REPL screen by sending the appropriate command to the terminal.
    def clear(self) -> Response:
        try:
            os.system("clear")  # Clear the screen for Unix/Linux/Mac
            
            return Response(status="success", message="Screen cleared")
        except Exception as e:
            return Response(status="error", message=f"Failed to clear screen: {str(e)}", code="ERR_CLEAR")
        
    def rm(self, request: Request) -> Request:
        try:
            path =  os.path.abspath(os.path.join(self.local_working_directory, ((request.local_path or request.remote_path) or '')))

            if not 'r' in request.options:
                os.remove(path)
            else:
                os.removedirs(path)
            return Response(status="success", message=f"Removed: {request.local_path or request.remote_path}")
        except FileNotFoundError:                                 # Handle cases where the path is invalid
            return Response(status="error", message=f"Invalid path {path}.", code="ERR_INVALID_PATH")
        except PermissionError:                                   # Handle cases where permission is denied
            return Response(status="error", message=f"Permission denied for {path}.", code="ERR_PERMISSION_DENIED")

    def mv(self, request: Request) -> Request:
        try: 
            src = os.path.abspath((os.path.join(self.local_working_directory, request.local_path) or ''))
            dst = os.path.abspath((os.path.join(self.local_working_directory, request.remote_path) or ''))

            if os.path.isdir(dst):
                dst = os.path.join(dst, os.path.basename(src))

            os.rename(src, dst)
            return Response(status="success", message=f"Removed: {request.local_path or request.remote_path}")
        except FileNotFoundError:
            return Response(status="error", message=f"Invalid path {src}.", code="ERR_INVALID_PATH")
        except PermissionError:
            return Response(status="error", message=f"Permission denied for {src}.", code="ERR_PERMISSION_DENIED")
        except OSError:
            return Response(status="error", message=f"Destination path {dst} exists", code="ERR_FILE_EXISTS")

    # touch
    # Creates an empty file at the specified path or updates the timestamp of an existing file.
    def touch(self, request: Request) -> Response:
        try:
            path = os.path.abspath(os.path.join(self.local_working_directory, ((request.local_path or request.remote_path) or '')))

            with open(path, "a"):
                os.utime(path, None) 
            
            return Response(status="success", message=f"File {path} created or timestamp updated")
        except PermissionError:
            return Response(status="error", message=f"Permission denied for {path}", code="ERR_PERMISSION_DENIED")
        except FileNotFoundError:
            return Response(status="error", message=f"Invalid path {path}", code="ERR_INVALID_PATH")
        except Exception as e:
            return Response(status="error", message=f"Failed to touch file {path}: {str(e)}", code="ERR_TOUCH")
        
    def cat(self, request: Request) -> Response:
        try:
            path = os.path.abspath(os.path.join(self.local_working_directory, ((request.local_path or request.remote_path) or '')))

            with open(path, "r") as file:
                contents = file.read()
            return Response(status="success", message=contents)
        except FileNotFoundError:
            return Response(status="error", message=f"File '{path}' not found.", code="ERR_FILE_NOT_FOUND")
        except PermissionError:
            return Response(status="error", message=f"Permission denied for '{path}'.", code="ERR_PERMISSION_DENIED")

    # ls
    # Lists the request directory files.
    # Builds `Response.contents` containing size, name, and type of the entries.
    # Accepts a `Request` object, which specifies the directory path.
    def ls(self, request: Request) -> Response:
        try:
            if request.cmd == 'get':
                path = os.path.abspath(os.path.join(self.local_working_directory, request.remote_path))
            else:
                path = os.path.abspath(os.path.join(self.local_working_directory, ((request.local_path or request.remote_path) or '')))

            entries = []

            if os.path.isfile(path):  # If the path is a file, process it directly
                stats = os.stat(path)

                mode = stat.filemode(stats.st_mode)
                nlink = stats.st_nlink
                user = pwd.getpwuid(stats.st_uid).pw_name
                group = grp.getgrgid(stats.st_gid).gr_name
                size = stats.st_size

                mtime = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
                entries.append(Content(mode=mode, nlink=nlink, user=user, group=group, size=size, mtime=mtime, name=os.path.basename(path)))
            else:  # Otherwise, treat it as a directory and list its contents
                for entry in os.scandir(path): 
                    stats = entry.stat() 

                    mode = stat.filemode(stats.st_mode)
                    nlink = stats.st_nlink
                    user = pwd.getpwuid(stats.st_uid).pw_name
                    group = grp.getgrgid(stats.st_gid).gr_name
                    size = stats.st_size

                    mtime = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
                    entries.append(Content(mode=mode, nlink=nlink, user=user, group=group, size=size, mtime=mtime, name=entry.name))

            # Sort entries alphabetically by name (case-insensitive)
            entries = sorted(entries, key=lambda x: x.name.lower())

            return Response(status="success", contents=entries)  # Return success response with sorted entries
        except FileNotFoundError:  # Handle cases where the directory doesn't exist
            return Response(status="error", message=f"Directory {path} not found", contents=[], code="ERR_DIR_NOT_FOUND")
        except PermissionError:  # Handle cases where access is denied
            return Response(status="error", message=f"Permission denied for {path}", contents=[], code="ERR_PERMISSION_DENIED")

    # pwd
    # Returns the current working directory as the `Response.message`.
    def pwd(self) -> Response:
        return Response(status="success", message=self.local_working_directory)

    # mkdir
    # Creates a new directory in the requested path.
    # Joins the current working directory with the requested.local_path (client) if set, 
    # or uses remote_path (server) if local_path is not set.
    def mkdir(self, request: Request) -> Response:
        try:
            path =  os.path.abspath(os.path.join(self.local_working_directory, ((request.local_path or request.remote_path) or '')))
            if not 'r' in request.options: 
                os.mkdir(path)
            else:
                os.makedirs(path)
            return Response(status="success", message=f"Directory '{request.local_path or request.remote_path}' created")
        except FileExistsError:                                   # Handle cases where the directory already exists
            return Response(status="error", message=f"Directory '{request.local_path or request.remote_path}' already exists.", code="ERR_DIR_EXISTS")
        except FileNotFoundError:                                 # Handle cases where the path is invalid
            return Response(status="error", message=f"Invalid path {path}", code="ERR_INVALID_PATH")
        except PermissionError:                                   # Handle cases where permission is denied
            return Response(status="error", message=f"Permission denied for {path}", code="ERR_PERMISSION_DENIED")

    # cd
    # Changes the current working directory.
    # Joins the current working directory with the requested.local_path (client) if set, 
    # or uses remote_path (server) if local_path is not set.
    def cd(self, request: Request) -> Response:
        try:            
            path = normalize_path(self.local_working_directory + '/' + (request.local_path or request.remote_path))

            # Check if the resolved path is a valid directory
            if os.path.isdir(path):
                os.chdir(path)  # Change the current working directory
                self.local_working_directory = os.getcwd()  # Update the tracked working directory
                return Response(status="success", message=f"Changed directory to {self.local_working_directory}")
            else:
                return Response(status="error", message=f"{path} is not a valid directory", code="ERR_INVALID_DIR")
        except Exception as e:
            # Catch unexpected errors and return an error response
            return Response(status="error", message=f"Failed to change directory: {str(e)}", code="ERR_CD")

    # get
    # One of four methods in this class that handles the send and recv logic for the user.
    # Sends the `Request` to the server, receives the `Response`, and writes binary data (if any) to a local file.
    def get(self, conn, request: Request) -> Response:
        path = normalize_path(request.local_path)

        try:
            self.send_all(conn, request)                          # Send the `Request` to the server
            response = self.recv_all(conn, Response)              # Receive the `Response` from the server

            if response.status == "success":
                for entry in response.contents:
                    path += '/' + entry.name
                    with open(path, "wb") as file:
                        file.write(response.get_binary_data())

            return self.recv_all(conn, Response)  # Return the server's response
        except Exception as e:
            return Response(status="error", message=f"Failed to download file {request.remote_path}: {str(e)}", code="ERR_GET_CLIENT")

    # put
    # Two of four methods in this class that handles the send and recv logic for the user.
    # Sends a file to the server by attaching binary data to the `Request`.
    # Sends the `Request`, then waits for the server's `Response`.
    def put(self, conn, request: Request) -> Response:
        try:
            path = normalize_path(request.local_path)

            with open(path, "rb") as file:          # Open the file in binary mode for reading
                binary_data = file.read()                         # Read the file's binary data

            request.size = len(binary_data)                       # Set the size property in the `Request`
            self.send_all(conn, request)                          # Send the `Request` with metadata and binary data

            response = self.recv_all(conn, Response)              # Receive the `Response` from the server
            if response.status == 'success':
                conn.sendall(binary_data)
        
            return self.recv_all(conn, Response)
        except Exception as e:
            return Response(status="error", message=f"Failed to send file {request.local_path}: {str(e)}", code="ERR_PUT_CLIENT")

    # put logic for server
    def receive_file(self, request: Request) -> Response:
        path = normalize_path(request.remote_path + '/' + request.local_path)

        try:
            if request.size <= 0:
                raise ValueError("Invalid file size in the request.")

            with open(path, "wb") as file:           # open received path in write binary mode
                file.write(request.get_binary_data())               # write binary data to file
            
            return Response(status="success", message=f"File {request.remote_path} received successfully.")
        except Exception as e:
            # Respond with error in case of failure
            return Response(status="error", message=f"Failed to save file '{path}': {str(e)}", code="ERR_PUT_SERVER")

    # get logic for server
    def send_file(self, conn, request: Request) -> Response:
        path = normalize_path(request.remote_path)
        try:
            res = self.ls(request)

            print(res)
            if res.status != 'success':
                raise

            with open(path, "rb") as file:                          # open requested path in read binary mode
               binary_data = file.read()                           # read binary data from file

            ack = Response(status="success", contents=res.contents, size=len(binary_data))
            self.send_all(conn, ack)
            response = self.recv_all(conn, Response)

            if response.status == "success":
                conn.sendall(binary_data)

            return Response(status="success", message=f"File {request.remote_path} sent successfully.")
        except Exception as e:
            return Response(status="error", message=f"Failed to send file '{request.remote_path}': {str(e)}", code="ERR_GET_SERVER")

    # send_all
    # Sends a `CustomProtocol` object (either `Request` or `Response`) and optional binary data over the socket.
    def send_all(self, conn, obj: CustomProtocol) -> None:
        try:
            json_payload = obj.prepare()                         # Prepare the object (validate and encode to JSON)
            conn.sendall(json_payload)                           # Send the JSON payload over the socket
        except Exception as e:
            print(f"Error sending data: {e}")
            raise

    # recv_all
    # Receives JSON metadata and optional binary data from the socket.
    # Dynamically constructs and returns the specified `CustomProtocol` object type (e.g., `Request` or `Response`).
    def recv_all(self, conn, obj_type: Type[CustomProtocol]) -> CustomProtocol:
        try:
            buffer = b""                                         # Allocate space for the buffer
            while not buffer.decode('utf-8').strip().endswith('}'):  # Read bytes until the message ends with '}'
                buffer += conn.recv(4096)

            obj = obj_type.decode(buffer, obj_type)              # Decode the buffer into the given obj_type

            if hasattr(obj, 'size') and obj.size > 0: # Check if the size property indicates incoming binary data
                response = Response(status="success", message="Awaiting binary data")
                self.send_all(conn, response)
                binary_data = b""                                # Allocate space for the binary data buffer
                size = obj.size 
                bytes_remaining = size                   # Determine the number of bytes to receive
                while bytes_remaining > 0:
                    chunk = conn.recv(min(4096, bytes_remaining)) # Receive data in chunks
                    if not chunk:
                        raise ConnectionError("Connection lost while receiving binary data.")
                    binary_data += chunk
                    bytes_remaining -= len(chunk)               # Update the remaining bytes to receive
                obj.attach_binary_data(binary_data)             # Attach the received binary data to the object

                if len(binary_data) != size:                # Validate the binary data size
                    raise ValueError(f"Binary data size mismatch: expected {obj.size}, got {len(binary_data)}.")

            obj.validate()

            return obj                                           # Return the constructed object
        except Exception as e:
            print(f"Error receiving data: {e}")
            raise
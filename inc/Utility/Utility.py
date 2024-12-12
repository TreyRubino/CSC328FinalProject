# Trey Rubino

import os
import stat
import grp
import pwd
import shutil
from datetime import datetime
from typing import Type

from ..Model.Request import Request
from ..Model.Response import Response, Content
from ..Model.CustomProtocol import CustomProtocol
from .sec_check import normalize_path

class Utility:
    """
    Utility class that contains helper functions for both Server and Client to use.
    Handles all commands, as well as sending and receiving data over sockets.
    """

    def __init__(self):
        """
        Constructor that sets the current local working directory.
        """
        self.local_working_directory = os.getcwd()

    def help(self, request: Request = None) -> Response:
        """
        Provides a list of available commands and their descriptions, or a specific command's description if specified.

        Args:
            request (Request, optional): The `Request` object containing the `remote_path` to specify a command.

        Returns:
            Response: A success response containing the help text or an error response if the command is not found.
        """
        try:
            help_dict = {
                "exit": "Quit the application.",
                "help": "Display this help text.",
                "cd": "Change remote directory to 'path'. If 'path' is not specified, change to the session's starting directory.",
                "ls": "Display a remote directory listing of 'path' or the current directory if 'path' is not specified.",
                "mkdir": "Create a remote directory specified by 'path'.",
                "pwd": "Display the remote working directory.",
                "get": "Retrieve 'remote-path' and store it on the local machine. If 'local-path' is not specified, use the same name as on the remote machine. If the -R flag is specified, directories are copied recursively.",
                "put": "Upload 'local-path' and store it on the remote machine. If 'remote-path' is not specified, use the same name as on the local machine. If the -R flag is specified, directories are copied recursively.",
                "lcd": "Change local directory to 'path'. If 'path' is not specified, change to the user's home directory.",
                "lls": "Display local directory listing of 'path' or the current directory if 'path' is not specified.",
                "lmkdir": "Create a local directory specified by 'path'.",
                "lpwd": "Print the local working directory.",
            }

            if request and request.remote_path:
                command = request.remote_path.strip()
                if command in help_dict:
                    return Response(status="success", message=f"{command}: {help_dict[command]}")
                else:
                    return Response(status="error", message=f"Command '{command}' not found.", code="ERR_COMMAND_NOT_FOUND")

            help_text = "--------------------\n" \
                        "Remote Commands:\n" + \
                        "\n".join([f"  {cmd:<25}: {desc}" for cmd, desc in help_dict.items() if cmd not in ["lcd", "lls", "lmkdir", "lpwd"]]) + \
                        "\n\nLocal Commands:\n" + \
                        "\n".join([f"  {cmd:<25}: {desc}" for cmd, desc in help_dict.items() if cmd in ["lcd", "lls", "lmkdir", "lpwd"]])

            return Response(status="success", message=help_text)
        except Exception as e:
            return Response(status="error", message=f"Failed to generate help text: {str(e)}", code="ERR_HELP")

    def clear(self) -> Response:
        """
        Clears the REPL screen by sending the appropriate command to the terminal.

        Returns:
            Response: A success response if the screen is cleared or an error response if clearing fails.
        """
        try:
            os.system("clear")  # Clear the screen for Unix/Linux/Mac
            return Response(status="success", message="Screen cleared")
        except Exception as e:
            return Response(status="error", message=f"Failed to clear screen: {str(e)}", code="ERR_CLEAR")

    def rm(self, request: Request) -> Response:
        """
        Removes a file or directory specified in the request object.

        Args:
            request (Request): The request object containing the path to remove.

        Returns:
            Response: A success or error response indicating the result of the operation.
        """
        try:
            path = os.path.abspath(os.path.join(self.local_working_directory, ((request.local_path or request.remote_path) or '')))

            # Check if the path exists and handle file vs directory
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                if '-r' in request.options:
                    shutil.rmtree(path)
                else:
                    return Response(status="error", message=f"Cannot remove directory '{path}' without '-r' option.", code="ERR_IS_DIRECTORY")
            else:
                return Response(status="error", message=f"Invalid path {path}", code="ERR_INVALID_PATH")

            return Response(status="success", message=f"Removed: {request.local_path or request.remote_path}")
        except FileNotFoundError:
            return Response(status="error", message=f"Invalid path {path}", code="ERR_INVALID_PATH")
        except PermissionError:
            return Response(status="error", message=f"Permission denied for {path}.", code="ERR_PERMISSION_DENIED")
        except Exception as e:
            return Response(status="error", message=f"Failed to remove {path}: {str(e)}", code="ERR_REMOVE")

    def cat(self, request: Request) -> Response:
        """
        Reads and returns the contents of a file specified in the request object.

        Args:
            request (Request): The request object containing the file path.

        Returns:
            Response: A success response containing file contents or an error response if reading fails.
        """
        try:
            path = os.path.abspath(os.path.join(self.local_working_directory, ((request.local_path or request.remote_path) or ''))); 
            if os.path.isdir(path): 
                return Response(status="error", message=f"'{path}' is a directory, not a file.", code="ERR_IS_DIRECTORY"); 
        
            with open(path, "r") as file: 
                contents = file.read(); 
            return Response(status="success", message=contents)
        except FileNotFoundError: 
            return Response(status="error", message=f"File '{path}' not found.", code="ERR_FILE_NOT_FOUND")
        except PermissionError: 
            return Response(status="error", message=f"Permission denied for '{path}'.", code="ERR_PERMISSION_DENIED")

    def ls(self, request: Request) -> Response:
        """
        Lists directory contents or file details for the specified path in the request object.

        Args:
            request (Request): The request object containing the directory or file path.

        Returns:
            Response: A success response containing directory or file details, or an error response if listing fails.
        """
        try:
            path = os.path.abspath(os.path.join(self.local_working_directory, ((request.local_path or request.remote_path) or '')))
            entries = []

            if os.path.isfile(path):            # handle file
                stats = os.stat(path)
                mode = stat.filemode(stats.st_mode)
                nlink = stats.st_nlink
                user = pwd.getpwuid(stats.st_uid).pw_name
                group = grp.getgrgid(stats.st_gid).gr_name
                size = stats.st_size
                mtime = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
                entries.append(Content(mode=mode, nlink=nlink, user=user, group=group, size=size, mtime=mtime, name=os.path.basename(path)))
            else:                               # handle directory
                for entry in os.scandir(path):
                    stats = entry.stat()
                    mode = stat.filemode(stats.st_mode)
                    nlink = stats.st_nlink
                    user = pwd.getpwuid(stats.st_uid).pw_name
                    group = grp.getgrgid(stats.st_gid).gr_name
                    size = stats.st_size
                    mtime = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
                    entries.append(Content(mode=mode, nlink=nlink, user=user, group=group, size=size, mtime=mtime, name=entry.name))

            entries = sorted(entries, key=lambda x: x.name.lower())
            return Response(status="success", contents=entries)
        except FileNotFoundError:
            return Response(status="error", message=f"Directory {path} not found", contents=[], code="ERR_DIR_NOT_FOUND")
        except PermissionError:
            return Response(status="error", message=f"Permission denied for {path}", contents=[], code="ERR_PERMISSION_DENIED")

    def pwd(self) -> Response:
        """
        Returns the current working directory.

        Returns:
            Response: A success response containing the current working directory.
        """
        return Response(status="success", message=self.local_working_directory)

    def mkdir(self, request: Request) -> Response:
        """
        Creates a new directory as specified in the request object.

        Args:
            request (Request): The request object containing the directory path.

        Returns:
            Response: A success or error response indicating the result of the operation.
        """
        try:
            path = os.path.abspath(os.path.join(self.local_working_directory, ((request.local_path or request.remote_path) or '')))
            if '-r' not in request.options:
                os.mkdir(path)
            else:
                os.makedirs(path)
            return Response(status="success", message=f"Directory '{request.local_path or request.remote_path}' created")
        except FileExistsError:
            return Response(status="error", message=f"Directory '{request.local_path or request.remote_path}' already exists", code="ERR_DIR_EXISTS")
        except FileNotFoundError:
            return Response(status="error", message=f"Invalid path {path}", code="ERR_INVALID_PATH")
        except PermissionError:
            return Response(status="error", message=f"Permission denied for {path}", code="ERR_PERMISSION_DENIED")

    def cd(self, request: Request) -> Response:
        """
        Changes the current working directory to the specified path in the request object.

        Args:
            request (Request): The request object containing the directory path.

        Returns:
            Response: A success or error response indicating the result of the operation.
        """
        try:
            path = normalize_path(self.local_working_directory + '/' + (request.local_path or request.remote_path))
            if os.path.isdir(path):
                os.chdir(path)
                self.local_working_directory = os.getcwd()
                return Response(status="success", message=f"Changed directory to {self.local_working_directory}")
            else:
                return Response(status="error", message=f"{path} is not a valid directory", code="ERR_INVALID_DIR")
        except Exception as e:
            return Response(status="error", message=f"Failed to change directory: {str(e)}", code="ERR_CD")
        
    def get(self, conn, request: Request) -> Response:
        """
        Sends a `Request` to the server, receives the `Response`, and writes binary data (if any) to a local file.

        Args:
            conn: The connection object used to communicate with the server.
            request (Request): The `Request` object containing the file retrieval details.

        Returns:
            Response: The server's response or an error response if the operation fails.
        """
        try:
            path = os.path.abspath(os.path.join(self.local_working_directory, request.local_path))
            self.send_all(conn, request)                          # Send the `Request` to the server
            response = self.recv_all(conn, Response)              # Receive the `Response` from the server

            if response.status == "success":
                for entry in response.contents:
                    path += '/' + entry.name
                    if (response.size > 0):
                        with open(path, "wb") as file:
                            file.write(response.get_binary_data())
                    else: 
                       return Response(status="error", message=f"No data received for {entry.name}.")
            return self.recv_all(conn, Response)  # Return the server's response
        except Exception as e:
            return Response(status="error", message=f"Failed to download file {request.remote_path}: {str(e)}", code="ERR_GET_CLIENT")

    def put(self, conn, request: Request) -> Response:
        """
        Sends a file to the server by attaching binary data to the `Request`.

        Args:
            conn: The connection object used to communicate with the server.
            request (Request): The `Request` object containing the file upload details.

        Returns:
            Response: The server's response or an error response if the operation fails.
        """
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

    def receive_file(self, request: Request) -> Response:
        """
        Handles file reception on the server, saving the binary data to the specified path.

        Args:
            request (Request): The `Request` object containing file metadata and binary data.

        Returns:
            Response: A success response if the file is saved successfully or an error response otherwise.
        """
        try:
            path = normalize_path(request.remote_path + '/' + request.local_path)
            if request.size <= 0:
                raise ValueError("Invalid file size in the request.")

            with open(path, "wb") as file:           # open received path in write binary mode
                file.write(request.get_binary_data())               # write binary data to file
            
            return Response(status="success", message=f"File {request.local_path} received successfully.")
        except Exception as e:
            return Response(status="error", message=f"Failed to save file '{path}': {str(e)}", code="ERR_PUT_SERVER")

    def send_file(self, conn, request: Request) -> Response:
        """
        Handles file sending on the server, transmitting binary data to the client.

        Args:
            conn: The connection object used to communicate with the client.
            request (Request): The `Request` object specifying the file to send.

        Returns:
            Response: A success response if the file is sent successfully or an error response otherwise.
        """
        try:
            path = os.path.abspath(os.path.join(self.local_working_directory, request.remote_path))
            request.local_path = None
            res = self.ls(request)
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

    def send_all(self, conn, obj: CustomProtocol) -> None:
        """
        Sends a `CustomProtocol` object (either `Request` or `Response`) over the socket.

        Args:
            conn: The connection object used to communicate.
            obj (CustomProtocol): The object to be sent, encoded as JSON.

        Raises:
            Exception: If an error occurs during sending.
        """
        try:
            json_payload = obj.prepare()                         # Prepare the object (validate and encode to JSON)
            conn.sendall(json_payload)                           # Send the JSON payload over the socket
        except Exception as e:
            print(f"Error sending data: {e}")
            raise

    def recv_all(self, conn, obj_type: Type[CustomProtocol]) -> CustomProtocol:
        """
        Receives JSON metadata and optional binary data from the socket and constructs the specified object type.

        Args:
            conn: The connection object used to communicate.
            obj_type (Type[CustomProtocol]): The type of object to construct (e.g., `Request` or `Response`).

        Returns:
            CustomProtocol: The constructed object with all received data.

        Raises:
            Exception: If an error occurs during reception or object construction.
        """
        try:
            buffer = b""                                         # Allocate space for the buffer
            while not buffer.decode('utf-8').strip().endswith('}'):  # Read bytes until the message ends with '}'
                buffer += conn.recv(4096)

            obj = obj_type.decode(buffer, obj_type)              # Decode the buffer into the given obj_type

            if hasattr(obj, 'size') and obj.size > 0: # Check if the size property indicates incoming binary data
                response = Response(status="success", message="Awaiting binary data...")
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
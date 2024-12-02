# Trey Rubino 

# Common functionality.

import os
from typing import Type
from ..Model.Request import Request
from ..Model.Response import Response, Content
from ..Model.CustomProtocol import CustomProtocol

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

    def help(self) -> Response:
        try:
            help_text = (
                "--------------------\n"
                "Remote Commands:\n"
                "  exit                     : Quit the application.\n"
                "  help                     : Display this help text.\n"
                "  cd [path]                : Change remote directory to 'path'. If 'path' is not specified, change to the session's starting directory.\n"
                "  ls [path]                : Display a remote directory listing of 'path' or the current directory if 'path' is not specified.\n"
                "  mkdir path               : Create a remote directory specified by 'path'.\n"
                "  pwd                      : Display the remote working directory.\n"
                "  get [-R] remote-path [local-path]\n"
                "                           : Retrieve 'remote-path' and store it on the local machine. If 'local-path' is not specified, use the same name as on the remote machine.\n"
                "                             If the -R flag is specified, directories are copied recursively.\n"
                "  put [-R] local-path [remote-path]\n"
                "                           : Upload 'local-path' and store it on the remote machine. If 'remote-path' is not specified, use the same name as on the local machine.\n"
                "                             If the -R flag is specified, directories are copied recursively.\n"
                "\n"
                "Local Commands:\n"
                "  lcd [path]               : Change local directory to 'path'. If 'path' is not specified, change to the user's home directory.\n"
                "  lls [path]               : Display local directory listing of 'path' or the current directory if 'path' is not specified.\n"
                "  lmkdir path              : Create a local directory specified by 'path'.\n"
                "  lpwd                     : Print the local working directory.\n"
            )
            return Response(status="success", message=help_text)
        except Exception as e:
            return Response(status="error", message=f"Failed to generate help text: {str(e)}", code="ERR_HELP")
        
    # ls
    # Lists the request directory files.
    # Builds `Response.contents` containing size, name, and type of the entries.
    # Accepts a `Request` object, which specifies the directory path.
    def ls(self, request: Request) -> Response:
        path = request.local_path or self.local_working_directory  # Use local_path or default to the current directory
        try:
            entries = []
            for entry in os.scandir(path):                         # Scan the directory for entries
                # Append each entry to `Response.contents` with details (size, name, type)
                entries.append(Content(size=entry.stat().st_size, name=entry.name, type="dir" if entry.is_dir() else "file"))
            return Response(status="success", contents=entries)  # Return success response with directory entries
        except FileNotFoundError:                                  # Handle cases where the directory doesn't exist
            return Response(status="error", message=f"Directory '{path}' not found.", contents=[], code="ERR_DIR_NOT_FOUND")
        except PermissionError:                                    # Handle cases where access is denied
            return Response(status="error", message=f"Permission denied for '{path}'.", contents=[], code="ERR_PERMISSION_DENIED")

    # pwd
    # Returns the current working directory as the `Response.message`.
    def pwd(self) -> Response:
        return Response(status="success", message=self.local_working_directory)

    # mkdir
    # Creates a new directory in the requested path.
    # Joins the current working directory with the requested.local_path (client) if set, 
    # or uses remote_path (server) if local_path is not set.
    def mkdir(self, request: Request) -> Response:
        path = os.path.abspath(os.path.join(self.local_working_directory, request.local_path or request.remote_path))
        try:
            if request.recursive: 
                os.makedirs(path)
            else:
                os.mkdir(path)
            return Response(status="success", message=f"Directory '{request.local_path or request.remote_path}' created.")
        except FileExistsError:                                   # Handle cases where the directory already exists
            return Response(status="error", message=f"Directory '{request.local_path or request.remote_path}' already exists.", code="ERR_DIR_EXISTS")
        except FileNotFoundError:                                 # Handle cases where the path is invalid
            return Response(status="error", message=f"Invalid path '{path}'.", code="ERR_INVALID_PATH")
        except PermissionError:                                   # Handle cases where permission is denied
            return Response(status="error", message=f"Permission denied for '{path}'.", code="ERR_PERMISSION_DENIED")

    # cd
    # Changes the current working directory.
    # Joins the current working directory with the requested.local_path (client) if set, 
    # or uses remote_path (server) if local_path is not set.
    def cd(self, request: Request) -> Response:
        path = os.path.abspath(os.path.join(self.local_working_directory, request.local_path or request.remote_path))
        if os.path.isdir(path):                                   # Check if the target path is a valid directory
            self.local_working_directory = path                   # Update the current working directory
            return Response(status="success", message=f"Changed directory to '{self.local_working_directory}'.")
        else:
            return Response(status="error", message=f"'{path}' is not a valid directory.", code="ERR_INVALID_DIR")
        
    # get
    # One of four methods in this class that handles the send and recv logic for the user.
    # Sends the `Request` to the server, receives the `Response`, and writes binary data (if any) to a local file.
    def get(self, conn, request: Request) -> Response:
        try:
            self.send_all(conn, request)                          # Send the `Request` to the server

            response = self.recv_all(conn, Response)              # Receive the `Response` from the server

            if response.status == "success":                      # If successful, write the binary data to a file
                with open(request.local_path, "wb") as file:
                    file.write(response.get_binary_data())

            return response                                       # Return the server's response
        except Exception as e:
            return Response(status="error", message=f"Failed to download file '{request.remote_path}': {str(e)}", code="ERR_GET_CLIENT")

    # put
    # Two of four methods in this class that handles the send and recv logic for the user.
    # Sends a file to the server by attaching binary data to the `Request`.
    # Sends the `Request`, then waits for the server's `Response`.
    def put(self, conn, request: Request) -> Response:
        try:
            with open(request.local_path, "rb") as file:          # Open the file in binary mode for reading
                binary_data = file.read()                         # Read the file's binary data

            request.size = len(binary_data)                       # Set the size property in the `Request`
            request.attach_binary_data(binary_data)               # Attach the binary data to the `Request`

            self.send_all(conn, request)                          # Send the `Request` with metadata and binary data

            return self.recv_all(conn, Response)                  # Receive the `Response` from the server
        except Exception as e:
            return Response(status="error", message=f"Failed to send file '{request.local_path}': {str(e)}", code="ERR_PUT_CLIENT")

    # put logic for server
    def receive_file(self, request: Request) -> Response:
        try:
            if request.size <= 0:
                raise ValueError("Invalid file size in the request.")
            
            with open(request.remote_path, "wb") as file:           # open received path in write binary mode
                file.write(request.get_binary_data())               # write binary data to file
            
            return Response(status="success", message=f"File '{request.remote_path}' received successfully.")
        except Exception as e:
            # Respond with error in case of failure
            return Response(status="error", message=f"Failed to save file '{request.remote_path}': {str(e)}", code="ERR_PUT_SERVER")

    # get logic for server
    def send_file(self, conn, request: Request) -> Response:
        try:
            with open(request.remote_path, "rb") as file:           # open requested path in read binary mode
                binary_data = file.read()                           # read binary data from file
            
            response = Response(status="success", message=f"File '{request.remote_path}' sent successfully.", name=request.remote_path, size=len(binary_data))
            response.attach_binary_data(binary_data)

            self.send_all(conn, response)                           # send response
            return response
        except Exception as e:
            return Response(status="error", message=f"Failed to send file '{request.remote_path}': {str(e)}", code="ERR_GET_SERVER")

    # send_all
    # Sends a `CustomProtocol` object (either `Request` or `Response`) and optional binary data over the socket.
    def send_all(self, conn, obj: CustomProtocol) -> None:
        try:
            json_payload = obj.prepare()                         # Prepare the object (validate and encode to JSON)
            conn.sendall(json_payload)                           # Send the JSON payload over the socket

            binary_data = obj.get_binary_data()                  # Check for binary data
            if binary_data:
                conn.sendall(binary_data)                        # If present, send the binary data
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

            obj = obj_type.decode(buffer, obj_type)              # Decode the buffer into the given `obj_type`

            if hasattr(obj, 'size') and obj.size > 0:            # Check if the `size` property indicates incoming binary data
                binary_data = b""                                # Allocate space for the binary data buffer
                bytes_remaining = obj.size                      # Determine the number of bytes to receive
                while bytes_remaining > 0:
                    chunk = conn.recv(min(4096, bytes_remaining)) # Receive data in chunks
                    if not chunk:
                        raise ConnectionError("Connection lost while receiving binary data.")
                    binary_data += chunk
                    bytes_remaining -= len(chunk)               # Update the remaining bytes to receive
                obj.attach_binary_data(binary_data)             # Attach the received binary data to the object

                if len(binary_data) != obj.size:                # Validate the binary data size
                    raise ValueError(f"Binary data size mismatch: expected {obj.size}, got {len(binary_data)}.")

            obj.validate()

            return obj                                           # Return the constructed object
        except Exception as e:
            print(f"Error receiving data: {e}")
            raise

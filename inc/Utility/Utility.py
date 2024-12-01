# Trey Rubino 

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
            return Response(status="success", contents=entries, code=None)  # Return success response with directory entries
        except FileNotFoundError:                                  # Handle cases where the directory doesn't exist
            return Response(status="error", message=f"Directory '{path}' not found.", contents=[], code="ERR_DIR_NOT_FOUND")
        except PermissionError:                                    # Handle cases where access is denied
            return Response(status="error", message=f"Permission denied for '{path}'.", contents=[], code="ERR_PERMISSION_DENIED")

    # pwd
    # Returns the current working directory as the `Response.message`.
    def pwd(self, request: Request) -> Response:
        return Response(status="success", message=self.local_working_directory, code=None)

    # mkdir
    # Creates a new directory in the requested path.
    # Joins the current working directory with the requested.local_path (client) if set, 
    # or uses remote_path (server) if local_path is not set.
    def mkdir(self, request: Request) -> Response:
        path = os.path.abspath(os.path.join(self.local_working_directory, request.local_path or request.remote_path))
        try:
            os.mkdir(path)                                         # Create the directory at the specified path
            return Response(status="success", message=f"Directory '{request.local_path or request.remote_path}' created.", code=None)
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
            return Response(status="success", message=f"Changed directory to '{self.local_working_directory}'.", code=None)
        else:
            return Response(status="error", message=f"'{path}' is not a valid directory.", code="ERR_INVALID_DIR")

    # get
    # One of two methods in this class that handles the send and recv logic for the user.
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
    # Two of tow methods in this class that handles the send and recv logic for the user.
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

            return obj                                           # Return the constructed object
        except Exception as e:
            print(f"Error receiving data: {e}")
            raise

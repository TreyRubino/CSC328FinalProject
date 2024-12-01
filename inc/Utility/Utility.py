# Trey Rubino

import os
from typing import Type
from Model import Request, Response, CustomProtocol, Content

class Utility:
    def __init__(self):
        self.local_working_directory = os.getcwd()

    def ls(self, request: Request) -> Response:
        path = request.local_path or self.local_working_directory
        try:
            entries = []
            for entry in os.scandir(path):
                entries.append(Content(size=entry.stat().st_size, name=entry.name, type="dir" if entry.is_dir() else "file"))
            return Response(status="success", contents=entries, code=None)
        except FileNotFoundError:
            return Response(status="error", message=f"Directory '{path}' not found.", contents=[], code="ERR_DIR_NOT_FOUND")
        except PermissionError:
            return Response(status="error", message=f"Permission denied for '{path}'.", contents=[], code="ERR_PERMISSION_DENIED")

    def pwd(self, request: Request) -> Response:
        return Response(status="success", message=self.local_working_directory, code=None)

    def mkdir(self, request: Request) -> Response:
        path = os.path.join(self.local_working_directory, request.local_path)
        try:
            os.mkdir(path)
            return Response(status="success", message=f"Directory '{request.local_path}' created.", code=None)
        except FileExistsError:
            return Response(status="error", message=f"Directory '{request.local_path}' already exists.", code="ERR_DIR_EXISTS")
        except FileNotFoundError:
            return Response(status="error", message=f"Invalid path '{path}'.", code="ERR_INVALID_PATH")
        except PermissionError:
            return Response(status="error", message=f"Permission denied for '{path}'.", code="ERR_PERMISSION_DENIED")

    def cd(self, request: Request) -> Response:
        path = os.path.abspath(os.path.join(self.local_working_directory, request.local_path))
        if os.path.isdir(path):
            self.local_working_directory = path
            return Response(status="success", message=f"Changed directory to '{self.local_working_directory}'.", code=None)
        else:
            return Response(status="error", message=f"'{path}' is not a valid directory.", code="ERR_INVALID_DIR")
        
    def get(self, conn: socket.socket, request: Request) -> Response:
        try:
            self.send_all(conn, request)

            response = self.recv_all(conn, Response)

            if response.status == "success":
                with open(request.local_path, "wb") as file:
                    file.write(response.get_binary_data())

            return response
        except Exception as e:
            return Response(status="error", message=f"Failed to download file '{request.remote_path}': {str(e)}", code="ERR_GET_CLIENT")
 
    def put(self, conn: socket.socket, request: Request) -> Response:
        try:
            with open(request.local_path, "rb") as file:
                binary_data = file.read()
            request.size = len(binary_data)
            request.attach_binary_data(binary_data)

            # Send the Request to the server
            self.send_all(conn, request)

            return self.recv_all(conn, Response)
        except Exception as e:
            return Response(status="error", message=f"Failed to send file '{request.local_path}': {str(e)}", code="ERR_PUT_CLIENT")

    def send_all(self, conn: socket.socket, obj: CustomProtocol) -> None:
        try:
            json_payload = obj.prepare()
            conn.sendall(json_payload)  

            binary_data = getattr(obj, 'binary_data', None)
            if binary_data:
                conn.sendall(binary_data) 
        except Exception as e:
            print(f"Error sending data: {e}")
            raise

    def recv_all(self, conn: socket.socket, obj_type: Type[CustomProtocol]) -> CustomProtocol:
        try:
            buffer = b""
            while not buffer.decode('utf-8').strip().endswith('}'):
                buffer += conn.recv(4096)

            obj = obj_type.decode(buffer, obj_type)

            if hasattr(obj, 'size') and obj.size > 0:
                binary_data = b""
                bytes_remaining = obj.size
                while bytes_remaining > 0:
                    chunk = conn.recv(min(4096, bytes_remaining))
                    if not chunk:
                        raise ConnectionError("Connection lost while receiving binary data.")
                    binary_data += chunk
                    bytes_remaining -= len(chunk)
                obj.attach_binary_data(binary_data)

                if len(binary_data) != obj.size:
                    raise ValueError(f"Binary data size mismatch: expected {obj.size}, got {len(binary_data)}.")

            return obj
        except Exception as e:
            print(f"Error receiving data: {e}")
            raise


    
    

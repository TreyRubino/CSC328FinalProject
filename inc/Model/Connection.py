# Trey Rubino

from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class Connection:
    """
    Represents a client's connection to the server, encapsulating connection details
    such as IP address, file descriptor, start time, last executed command, connection
    duration, and current working directory.

    This class allows efficient tracking and management of client data for purposes such
    as server shutdowns, monitoring, and security measures.
    """
    ip_address: str
    fd: int
    start_time: datetime
    last_command: str
    connection_length: int
    current_working_directory: str

    def __init__(self, ip_address: str, fd: int):
        """
        Initializes a new client connection with the given IP address and file descriptor.

        Args:
            ip_address (str): The IP address of the client.
            fd (int): The file descriptor representing the client's connection.

        Attributes:
            start_time (datetime): The timestamp when the connection was established.
            last_command (str): The last command issued by the client (default: None).
            current_working_directory (str): The client's current working directory (default: None).
            connection_length (int): Duration of the connection in seconds (default: 1).
        """
        self.ip_address = ip_address        # IP address of the client
        self.fd = fd                        # File Descriptor (unique connection identifier)
        self.start_time = datetime.now()    # Connection start time
        self.last_command = None            # The last command issued by the client
        self.current_working_directory = None  # Current directory on the client's side
        self.connection_length = 1          # Connection length in seconds (default: 1)

    def update_connection(self, command: str = None, pwd: str = None):
        """
        Updates the connection details, such as the last command and current directory.

        Args:
            command (str, optional): The latest command executed by the client.
            pwd (str, optional): The current working directory of the client.
        """
        self.connection_length = int((datetime.now() - self.start_time).total_seconds())
        self.last_command = command
        self.current_working_directory = pwd

    def to_dict(self) -> dict:
        """
        Converts the connection object into a dictionary for easier serialization or logging.

        Returns:
            dict: A dictionary representation of the connection object, including the following keys:
                - client_id: The process ID (PID) of the current server process.
                - ip_address: The IP address of the client.
                - connection_length: The duration of the connection in seconds.
                - last_command: The last command executed by the client.
                - start_time: The connection's start time as an ISO-formatted string.
                - current_working_directory: The current working directory of the client.
        """
        connection_data = {
            "client_id": os.getpid(),  # Process ID representing the client
            "ip_address": self.ip_address,
            "connection_length": self.connection_length,
            "last_command": self.last_command,
            "start_time": self.start_time.isoformat(),
            "current_working_directory": self.current_working_directory
        }
        return connection_data

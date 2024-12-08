# Trey Rubino

# These are model classes, an object (data structure) of the custom Response of our protocol.
# To access properties of this class, use the `.` member access operator on an instance of this class.

from dataclasses import dataclass
from datetime import datetime

# Basic but dynamic representation of our protocols client connections.
# This model class can be used by our server to neatly and efficiently represent a connected client.
# Usage of this class can make it easy to keep track of all clients connected and manage their data efficiently.
# This can include last commands executed, ip address, fds, connect lengths. This can be used for server shut downs, 
# as well as security measures.
@dataclass
class Connection:
    ip_address: str
    fd: int
    start_time: datetime
    last_command: str 
    connection_length: int

    def __init__(self, ip_address, fd):
        self.ip_address = ip_address        # IP address of the client
        self.fd = fd                        # File Descriptor (unique connection identifier)
        self.start_time = datetime.now()    # Connection start time
        self.last_command = None            # The last command issued by the client
        self.current_working_directory

    def update(self, command=None, pwd=None):
        self.connection_length = (datetime.now() - self.start_time).total_seconds()
        if command != None:
            self.last_command = command
        elif pwd != None:
            self.current_working_directory = pwd

    def to_dict(self):
        connection_data = {
            "client_id": self.fd.fileno(),
            "ip_address": self.ip_address,
            "connection_length": self.connection_length,
            "last_command": self.last_command,
            "start_time": self.start_time.isoformat(),
        }
        return connection_data

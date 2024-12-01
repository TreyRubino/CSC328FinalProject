# Trey Rubino

# These are model classes, and object (data structure) of the custom Response of our protocol.
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
        self.connection_length = 1          # length of connection in seconds

    def update_connection_length(self):
        self.connection_length = (datetime.now() - self.start_time).total_seconds()

    def update_last_command(self, command):
        self.last_command = command

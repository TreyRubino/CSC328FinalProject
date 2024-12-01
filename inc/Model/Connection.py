# Trey Rubino

from dataclasses import dataclass
from datetime import datetime

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

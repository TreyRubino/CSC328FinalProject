# Trey Rubino

# These are model classes, and object (data structure) of the custom Response of our protocol.
# To access properties of this class, use the `.` member access operator on an instance of this class.

from dataclasses import dataclass
from typing import Optional
from .CustomProtocol import CustomProtocol

# Basic but dynamic representation of our protocols requests.
@dataclass
class Request(CustomProtocol):
    cmd: str
    remote_path: Optional[str] = None
    local_path: Optional[str] = None
    recursive: Optional[bool] = False
    size: Optional[int] = 0

    def validate(self):
        if not self.cmd:
            raise ValueError("Command (cmd) cannot be empty")



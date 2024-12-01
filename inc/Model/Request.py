# Trey Rubino

from dataclasses import dataclass
from typing import Optional
from CustomProtocol import CustomProtocol

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



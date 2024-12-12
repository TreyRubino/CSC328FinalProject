# Trey Rubino

from dataclasses import dataclass, field
from typing import Optional
from .CustomProtocol import CustomProtocol

@dataclass
class Request(CustomProtocol):
    """
    Represents the structure of a protocol request.

    Attributes:
        cmd (str): The command to be executed (e.g., "get", "put", "ls").
        options (Optional[list]): A list of options associated with the command (e.g., "-r").
        remote_path (Optional[str]): The remote file or directory path for the request.
        local_path (Optional[str]): The local file or directory path for the request.
        size (Optional[int]): The size of the data to be sent or received, in bytes.
    """
    cmd: str
    options: Optional[list] = field(default_factory=list)
    remote_path: Optional[str] = None
    local_path: Optional[str] = None
    size: Optional[int] = 0

    def validate(self):
        """
        Validates the Request instance.

        Raises:
            ValueError: If the `cmd` attribute is empty.
        """
        if not self.cmd:
            raise ValueError("Command (cmd) cannot be empty")

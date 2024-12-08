# Trey Rubino

# These are model classes, an object (data structure) of the custom Response of our protocol.
# To access properties of this class, use the `.` member access operator on an instance of this class.

from dataclasses import dataclass, field
from typing import List, Optional
from .CustomProtocol import CustomProtocol

# Content class is a helper structure to the response class.
# You can access these the same way with the '.' member access operator,
# but you can also loop over these since in the response `contents` is a,
# list of instances of this class.
@dataclass
class Content:
    mode: str         # File permissions (e.g., -rw-r--r--)
    nlink: int        # Number of links (1 for files, directory entry count for dirs)
    user: str         # Username of the owner
    group: str        # Group name of the owner
    size: int         # File size in bytes
    mtime: str        # Last modified date and time
    name: str         # File or directory name

# Basic but dynamic representation of our protocols responses.
@dataclass
class Response(CustomProtocol):
    status: str
    message: Optional[str] = None
    contents: Optional[List[Content]] = field(default_factory=list)
    code: Optional[str] = None
    size: Optional[int] = 0

    def validate(self): 
        if not self.status:
            raise ValueError("Status cannot be empty")


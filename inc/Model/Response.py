# Trey Rubino

from dataclasses import dataclass, field
from typing import List, Optional
from .CustomProtocol import CustomProtocol

@dataclass
class Content:
    """
    Represents a helper structure for file or directory metadata.

    Attributes:
        mode (str): File permissions in a string format (e.g., -rw-r--r--).
        nlink (int): Number of links. For files, this is usually 1. For directories, this is the entry count.
        user (str): Username of the file or directory owner.
        group (str): Group name of the file or directory owner.
        size (int): Size of the file in bytes.
        mtime (str): Last modified date and time as a string.
        name (str): The name of the file or directory.
    """
    mode: str
    nlink: int
    user: str
    group: str
    size: int
    mtime: str
    name: str

@dataclass
class Response(CustomProtocol):
    """
    Represents the structure of a protocol response.

    Attributes:
        status (str): The status of the response (e.g., "success", "error").
        message (Optional[str]): An optional message describing the response.
        contents (Optional[List[Content]]): A list of Content objects representing files or directories.
        code (Optional[str]): An optional error or status code.
        size (Optional[int]): Size of the data being sent or received in bytes.
    """
    status: str
    message: Optional[str] = None
    contents: Optional[List[Content]] = field(default_factory=list)
    code: Optional[str] = None
    size: Optional[int] = 0

    def validate(self):
        """
        Validates the Response instance.

        Raises:
            ValueError: If the `status` attribute is empty.
        """
        if not self.status:
            raise ValueError("Status cannot be empty")

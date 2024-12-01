# Trey Rubino

# These are model classes, and object (data structure) of the custom Response of our protocol.
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
    size: int
    name: str
    type: str

# Basic but dynamic representation of our protocols responses.
@dataclass
class Response(CustomProtocol):
    status: str
    message: Optional[str] = None
    contents: Optional[List[Content]] = field(default_factory=list)
    code: Optional[str] = None

    def validate(self): 
        if not self.status:
            raise ValueError("Status cannot be empty")


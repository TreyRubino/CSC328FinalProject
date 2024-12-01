# Trey Rubino

from dataclasses import dataclass, field
from typing import List, Optional
from CustomProtocol import CustomProtocol

@dataclass
class Content:
    size: int
    name: str
    type: str

@dataclass
class Response(CustomProtocol):
    status: str
    message: Optional[str] = None
    contents: Optional[List[Content]] = field(default_factory=list)

    def validate(self): 
        if not self.status:
            raise ValueError("Status cannot be empty")


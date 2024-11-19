from dataclasses import dataclass, field
from typing import List
import Protocol

@dataclass
class Content:
    size: int
    name: str
    type: str

@dataclass
class Response(Protocol):
    status: str
    message: str
    contents: List[Content] = field(default_factor = list)

    def validate(self):
        if not self.status: 
            raise ValueError("Status cannot be empty.")
        if not self.message:
            raise ValueError("Message cannot be empty.")

    def set_status(self, status: str):
        self.status = status
    
    def set_message(self, message: str):
        self.message = message

    def set_content(self, content: Content):
        self.contents.append(content)


from dataclasses import dataclass
import Protocol

@dataclass
class Request(Protocol):
    cmd: str
    remote_path: str
    local_path: str
    recursive: bool

    def set_cmd(self, cmd: str):
        self.cmd = cmd

    def set_remote_path(self, remote_path: str): 
        self.remote_path = remote_path

    def set_local_path(self, local_path: str):
        self.local_path = local_path

    def set_size(self, size: float):
        self.size = size
    
    def set_recursive(self, recursive: bool):
        self.recursive = recursive



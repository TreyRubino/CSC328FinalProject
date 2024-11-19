import Session
from Model import Connection

class ChildSession(Session):
    def __init__(self, connection: Connection, update_queue):
        self.connection = connection  
        self.update_queue = update_queue 

    def handle_command(self, command: str):
        super().handle_command(command)
        self.connection.last_command = command
        self.update_last_command(command)
        self.update_queue.put(self.connection)

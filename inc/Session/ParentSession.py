from Model import Connection
import Session

class ParentSession(Session):
    def __init__(self):
        super().__init__()
        self.connections = {} 

    def add_connection(self, client_id, connection):
        self.connections[client_id] = connection

    def update_connection(self, client_id, last_command):
        if client_id in self.connections:
            self.connections[client_id].update_last_command(last_command)
            self.connections[client_id].update_connection_length()

    def display_clients(self):
        print("\nConnected Clients:")
        print("-" * 60)
        for client_id, connection in self.connections.items():
            print(f"Client ID: {client_id}")
            print(f"  {connection}")
        print("-" * 60)

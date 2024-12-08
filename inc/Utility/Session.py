# Trey Rubino

from datetime import datetime

class Session():
    def __init__(self):
        self.connections = {} 

    def update_connections(self, client_id, connection):
        self.connections[client_id] = connection

    def display_clients(self):
        # If no clients are connected, print a simple message
        if not self.connections:
            print("\nNo connected clients at the moment.")
            return
        
        print("=" * 70)
        # Print table headers
        # Adjust spacing and column widths as needed
        print("{:<12} | {:<20} | {:<15} | {:<20}".format(
            "Client ID", "IP Address", "Conn Length", "Last Command"))
        print("-" * 70)

        for client_id, connection in self.connections.items():
            ip = connection['ip_address']
            start_time = datetime.fromisoformat(connection['start_time'])  # Parse the start_time string
            current_time = datetime.now()  # Get the current time
            connection_duration = (current_time - start_time).total_seconds()  # Calculate duration in seconds
            last_cmd = connection['last_command']
            print("{:<12} | {:<20} | {:<15} | {:<20}".format(
                client_id, str(ip), str(connection_duration), str(last_cmd)))

        print("=" * 70)

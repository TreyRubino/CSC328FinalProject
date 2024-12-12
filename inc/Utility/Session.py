# Trey Rubino

from datetime import datetime

class Session():
    """
    Manages client connections in a session, allowing updates, display, and cleanup of disconnected clients.
    """

    def __init__(self):
        """
        Initializes a Session instance with an empty dictionary to store client connections.
        """
        self.connections = {}

    def update_connections(self, client_id, connection):
        """
        Updates the session's connections with a new or existing client.

        Args:
            client_id (str): Unique identifier for the client.
            connection (dict): Connection details including IP address, start time, last command, and current working directory.
        """
        self.connections[client_id] = connection

    def display_clients(self):
        """
        Displays the details of all connected clients, including their connection duration, last command, and current directory.
        Removes clients that have issued the 'exit' command from the connections.

        Prints:
            Table of connected clients with the following columns:
            - Client ID
            - IP Address
            - Connection Length (in seconds)
            - Last Command
            - Current Directory
            If no clients are connected, prints a message indicating no connections.
        """
        if not self.connections:
            print("\nNo connected clients at the moment.")
            return

        print("=" * 90)
        print("{:<10} | {:<20} | {:<12} | {:<12} | {:<20}".format(
            "Client ID", "IP Address", "Conn Length", "Last Command", "Current Directory"))
        print("=" * 90)
        print("-" * 90)

        disconnected_clients = []
        for client_id, connection in self.connections.items():
            ip = connection['ip_address']
            start_time = datetime.fromisoformat(connection['start_time'])  # Parse the start_time string
            current_time = datetime.now()  # Get the current time
            connection_duration = (current_time - start_time).total_seconds()  # Calculate duration in seconds
            last_cmd = connection['last_command']
            current_directory = connection['current_working_directory']
            print("{:<10} | {:<20} | {:<12} | {:<12} | {:<20}".format(
                client_id, str(ip), str(connection_duration), str(last_cmd), str(current_directory)))
            print("-" * 90)

            if str(last_cmd) == 'exit':
                disconnected_clients.append(client_id)
        print("=" * 90)

        for client_id in disconnected_clients:
            del self.connections[client_id]

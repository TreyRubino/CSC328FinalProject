import os
import Server
from queue import Empty
from Session import ParentSession

class ServerController:
    def __init__(self):
        self.parent_session = ParentSession()

    def start(self):
        try:
            server = Server()

            server.bind("localhost", 22)
            server.listen()

            while True:
                connection = server.accept() 
                if connection:
                    print(f"Accepted connection: FD={connection.fd}, IP={connection.ip_address}")

                    self.parent_session.add_connection(connection.fd, connection)

                    self.poll_queue(server.get_queue())
                else:
                    print("No session accepted, continuing...")
        except Exception as e:
            print(f"An error has occurred: {e}")

    def poll_queue(self, queue):
        try:
            while True:
                connection_update = queue.get_nowait()          # Get updates from the queue without blocking
                self.parent_session.update_connection(
                    client_id=connection_update.fd,
                    last_command=connection_update.last_command,
                )
        except Empty:
            pass

        self.refresh_display()

    def refresh_display(self):
        self.clear_screen()
        self.parent_session.display_clients()

    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    def stop(self):
        pass

# Trey Rubino

import json
import time
import os

from ..Model.Connection import Connection

def read_pipe(read_fd, session):
    """
    Handles the reading of the child connection data
    """
    while True:
        try:
            raw_data = os.read(read_fd, 1024).decode('utf-8')
            if raw_data:
                connection_data = json.loads(raw_data)
                client_id = connection_data['client_id']
                session.update_connections(client_id, connection_data)

                os.system("clear")
                session.display_clients()
            else:
                # No data this instant, just wait briefly
                time.sleep(0.1)
        except BlockingIOError:
            # No data right now, keep trying
            time.sleep(0.1)
        except Exception as e:
            print(f"Error reading from pipe: {e}")

def update_session(write_fd, connection: Connection):
    """
    Handles writing updated connection data to the main session
    """
    try:
        if write_fd:  # Ensure write_fd is valid
            serialized_data = json.dumps(connection.to_dict())
            os.write(write_fd, serialized_data.encode('utf-8'))
    except BrokenPipeError:
        print("Pipe is broken; unable to send data to parent.")
    except Exception as e:
        print(f"Error sending connection to parent: {e}")
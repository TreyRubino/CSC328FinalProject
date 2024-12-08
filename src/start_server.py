#!/usr/bin/env python3

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from inc.Parser.serverP import parseArgs
from inc.fileserver import socketInfo
from inc.Utility.Session import Session
from inc.Utility.session_pipe import read_pipe

def main():
    try:
        read_fd, write_fd = os.pipe()

        pid = os.fork()  # Fork the process
        if pid == 0:
            # Child process: handle reading from the pipe
            os.close(write_fd)  # Close unused write end
            session = Session()
            read_pipe(read_fd, session)
            os._exit(0)
        else:
            # Parent process: handle socket communication
            os.close(read_fd)  # Close unused read end
            port, directory, directoryAbs = parseArgs(sys.argv[1:])
            socketInfo(port, directory, directoryAbs, write_fd)
            os.close(write_fd)  # Close write end when done
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        print("Killing...")
        sys.exit(0)
        
if __name__ == '__main__':
    main()

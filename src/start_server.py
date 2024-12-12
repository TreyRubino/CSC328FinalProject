#!/usr/bin/env python3

# Alexa Fisher
# Trey Rubino

import sys
import os
import time
import signal
import socket

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from inc.Parser.serverP import parseArgs
from inc.fileserver import socketInfo
from inc.Utility.Session import Session
from inc.Utility.session_pipe import read_pipe

#/************************************************************************/
#/*     Function Name:    main                                           */
#/*     Description:      Forks to start a session and have client       */
#/*                       things dealt with at the same time             */
#/*     Parameters:       none                                           */
#/*     Return Value:     none                                           */
#/************************************************************************/
def main():
    try:
        read_fd, write_fd = os.pipe()

        pid = os.fork()  # Fork the process
        if pid == 0:
            signal.signal(signal.SIGINT, killNicely)
            # Child process: handle reading from the pipe
            os.close(write_fd)  # Close unused write end
            session = Session()
            read_pipe(read_fd, session)
            os._exit(0)
        else:
            # Parent process: handle socket communication
            os.close(read_fd)  # Close unused read end
            port, _, directoryAbs = parseArgs(sys.argv[1:])
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', int(port)))  # Bind to the host and port
                s.listen()  # Start listening for incoming connections
                socketInfo(s, directoryAbs, write_fd)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        #sys.exit(0)
        pass

#/************************************************************************/
#/*     Function Name:    killNicely                                     */
#/*     Description:      Signal Handler to kill the server              */
#/*     Parameters:       signum - signal to watch for                   */
#/*                       frame - when the signal is recieved            */
#/*                       childCount - the number of children            */
#/*     Return Value:     none                                           */
#/************************************************************************/         
def killNicely(signum, frame):
    print("killing...")
    time.sleep(5)
    sys.exit(0)

if __name__ == '__main__':
    main()

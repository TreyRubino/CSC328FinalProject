#!/usr/bin/env python3

import sys
import os
import socket

from .Model.Response import Response
from .Model.Request import Request
from .Model.Connection import Connection

from .Utility.Utility import Utility
from .Utility.session_pipe import update_session
from .Utility.sec_check import normalize_path, is_within_root

#Citation:
# Author: Python Docs
# Source: https://docs.python.org/3.7/
# Retrieved November 26th, 2024

import os
import json
from .Model.Connection import Connection

def socketInfo(port, directory, directoryAbs, write_fd):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', int(port)))  # Bind to the host and port
            s.listen()  # Start listening for incoming connections

            while True:
                clientConn, clientAdd = s.accept()  # Accept a new client connection
                clientConnection = Connection(clientAdd, clientConn)

                pid = os.fork()  # Fork a new process
                if pid > 0:  # Parent process
                    clientConn.close()  # Close client socket in parent
                    while os.waitpid(-1, os.WNOHANG) > (0, 0):  # Clean up zombie processes
                        pass
                elif pid == 0:  # Child process
                    s.close()  # Close server socket in child
                    try:
                        # Send connection object to the parent process
                        update_session(write_fd=write_fd, connection=clientConnection)
                        #os.close(write_fd)  # Close write end after use in the child

                        # Handle client requests in the child process
                        childProcess(clientConnection.fd, directory, directoryAbs, write_fd, clientConnection)
                    except Exception as e:
                        print(f"Error in child process: {e}")
                    finally:
                        clientConnection.fd.close()
                    os._exit(0)
                else:
                    print("Fork failed")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sys.exit(1)

def childProcess(clientConn, directory, directoryAbs, write_fd, connection):
    try:
        utility = Utility()
        utility.local_working_directory = directoryAbs

        while True:
            clientRequest = utility.recv_all(clientConn, Request)

            connection.update(clientRequest.cmd, utility.local_working_directory)
            update_session(write_fd=write_fd, connection=connection)    # update the session

            if clientRequest.cmd == "exit":
                break
            getCommand(utility, clientRequest, clientConn, directory)

        os.close(write_fd)
        cleanUp(utility, clientConn)
            
    except Exception as e: #catch all other errors
        print(f"Error: {e}")
        sys.exit(1)

def getCommand(utility, request, clientConn, directory):
    if request.cmd == "get":
        #secPass = security(request.remote_path,directory)
        #if not secPass:
        #    failureResponse(utility, clientConn)
        #else:
        response = utility.send_file(clientConn, request)
        utility.send_all(clientConn, response)
    elif request.cmd == "ls":
        response = utility.ls(request)
        utility.send_all(clientConn, response)
    elif request.cmd == "mkdir":
        #secPass = security(request.remote_path,directory)
        #if not secPass:
        #    failureResponse(utility, clientConn)
        #else:
        response = utility.mkdir(request)
        utility.send_all(clientConn, response)
    elif request.cmd == "put":
        #secPass = security(request.remote_path,directory)
        #if not secPass:
        #    failureResponse(utility, clientConn)
        #else:
        response = utility.receive_file(request)
        utility.send_all(clientConn, response)
    elif request.cmd == "cd":
        #secPass = security(request.remote_path, directory)
        #if not secPass:
        #    failureResponse(utility, clientConn)
        #else:
        response = utility.cd(request)
        utility.send_all(clientConn, response)
    elif request.cmd == "pwd":
        response = utility.pwd()
        utility.send_all(clientConn, response)
    elif request.cmd == "rm":
        response = utility.rm(request)
        utility.send_all(clientConn, response)
    elif request.cmd == "mv":
        response = utility.mv(request)
        utility.send_all(clientConn, response)
    elif request.cmd == "touch":
        response = utility.rm(request)
        utility.send_all(clientConn, response)
    elif request.cmd == "cat":
        response = utility.cat(request)
        utility.send_all(clientConn, response)

def cleanUp(utility, clientConn):
    successResponse = Response(status="success", message="Exited Successfully")
    utility.send_all(clientConn, successResponse)

def security(filePath, directory):
    secCheck = True

    root = normalize_path(directory)
    target = normalize_path(os.path.join(root, filePath))

    if not is_within_root(root, target):
        secCheck = False

    return secCheck

def failureResponse(utility, clientConn):
    failure = Response(status="error", message="Permission Denied")
    utility.send_all(clientConn, failure)
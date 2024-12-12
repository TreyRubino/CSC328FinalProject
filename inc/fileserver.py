#!/usr/bin/env python3

# Alexa Fisher
# Trey Rubino

import sys
import os

from .Utility.Utility import Utility
from .Model.Response import Response
from .Model.Request import Request
from .Model.Connection import Connection

from .Utility.session_pipe import update_session
from .Utility.sec_check import normalize_path, is_within_root

#Citation:
# Author: Python Docs
# Source: https://docs.python.org/3.7/
# Retrieved November 26th, 2024

#/************************************************************************/
#/*     Function Name:    socketInfo                                     */
#/*     Description:      Creates server socket and accepts client       */
#/*                       connections                                    */
#/*     Parameters:       s - server socket file descriptor              */
#/*                       directory - user given directory               */
#/*                       directoryAbs - absolute path of the current    */
#/*                                      directory                       */
#/*                       write_fd - write end of session pipe           */
#/*     Return Value:     none                                           */
#/************************************************************************/
def socketInfo(s, directoryAbs, write_fd):
    try:
        while True:
            clientConn, clientAdd = s.accept()  # Accept a new client connection
            clientConnection = Connection(clientAdd, clientConn)

            pid = os.fork()  # Fork a new process
            if pid > 0:  # Parent process
                clientConn.close()  # Close client socket in parent
                while os.waitpid(-1, os.WNOHANG) > (0, 0):  # Clean up zombie processes
                    pass

            elif pid == 0:  # Child process
                try:
                    s.close()
                    # Send connection object to the parent process
                    update_session(write_fd=write_fd, connection=clientConnection)

                    # Handle client requests in the child process
                    childProcess(clientConnection.fd, directoryAbs, clientConnection, write_fd)
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
        pass

#/************************************************************************/
#/*     Function Name:    childProcess                                   */
#/*     Description:      All client things are done through this        */
#/*                       function                                       */
#/*     Parameters:       clientConn - client socket file descriptor     */
#/*                       directory - user given directory               */
#/*                       directoryAbs - absolute path of the current    */
#/*                                      directory                       */
#/*                       connection - object of the Connection class to */
#/*                                    keep track of each client         */
#/*                       write_fd - write end of session pipe           */
#/*     Return Value:     none                                           */
#/************************************************************************/
def childProcess(clientConn, directoryAbs, connection, write_fd):
    try:
        utility = Utility()
        utility.local_working_directory = directoryAbs

        while True:
            clientRequest = utility.recv_all(clientConn, Request)

            if clientRequest.cmd != "cd":
                connection.update_connection(command=clientRequest.cmd, pwd=utility.local_working_directory)
                update_session(write_fd=write_fd, connection=connection)    # update the session

            if clientRequest.cmd == "exit":
                break

            pipe_info = {
                'connection': connection,
                'write_fd'  : write_fd 
            }

            getCommand(utility, directoryAbs, clientRequest, clientConn, pipe_info)

        os.close(write_fd)
        cleanUp(utility, clientConn)
    except KeyboardInterrupt:
        response = Response(status="shutdown", message="Server shutting down in 5 seconds....")
        clientConn.sendall(response.prepare())
    except Exception as e: #catch all other errors
        print(f"Error: {e}")
        sys.exit(1)

#/************************************************************************/
#/*     Function Name:    getCommand                                     */
#/*     Description:      Switch statement for specific commands         */
#/*     Parameters:       utility - object of Utility class to send and  */
#/*                                 recieve responses and requests       */
#/*                       directory - user given directory               */
#/*                       request - the client request for a command     */
#/*                       clientConn - client socket file descriptor     */
#/*                       connection - object of the Connection class to */
#/*                                    keep track of each client         */
#/*                       write_fd - write end of session pipe           */
#/*     Return Value:     none                                           */
#/************************************************************************/
def getCommand(utility, directory, request, clientConn, pipe_info):
    if request.cmd == "get":
        secPass = security(request.remote_path, directory)
        if not secPass:
            failureResponse(utility, clientConn)
        else:
            response = utility.send_file(clientConn, request)
            utility.send_all(clientConn, response)
    elif request.cmd == "ls":
        response = utility.ls(request)
        utility.send_all(clientConn, response)
    elif request.cmd == "mkdir":
        secPass = security(request.remote_path,directory)
        if not secPass:
            failureResponse(utility, clientConn)
        else:
            response = utility.mkdir(request)
            utility.send_all(clientConn, response)
    elif request.cmd == "put":
        secPass = security(request.remote_path,directory)
        if not secPass:
            failureResponse(utility, clientConn)
        else:
            response = utility.receive_file(request)
            utility.send_all(clientConn, response)
    elif request.cmd == "cd":
        secPass = security(request.remote_path, directory)
        if not secPass:
            failureResponse(utility, clientConn)
        else:
            response = utility.cd(request)
            pipe_info['connection'].update_connection(command=request.cmd, pwd=utility.local_working_directory)           # update this clients last command
            update_session(write_fd=pipe_info['write_fd'], connection=pipe_info['connection'])    # update the session
            utility.send_all(clientConn, response)
    elif request.cmd == "pwd":
        response = utility.pwd()
        utility.send_all(clientConn, response)
    elif request.cmd == "rm":
        secPass = security(request.remote_path, directory)
        if not secPass:
            failureResponse(utility, clientConn)
        else:
            response = utility.rm(request)
            utility.send_all(clientConn, response)
    elif request.cmd == "cat":
        secPass = security(request.remote_path, directory)
        if not secPass:
            failureResponse(utility, clientConn)
        else:
            response = utility.cat(request)
            utility.send_all(clientConn, response)

#/************************************************************************/
#/*     Function Name:    cleanUp                                        */
#/*     Description:      If received exit command then clean up         */
#/*     Parameters:       utility - object of Utility class to send and  */
#/*                                 recieve responses and requests       */
#/*                       clientConn - client socket file descriptor     */
#/*     Return Value:     none                                           */
#/************************************************************************/
def cleanUp(utility, clientConn):
    successResponse = Response(status="success", message="Exited Successfully")
    utility.send_all(clientConn, successResponse)


#/************************************************************************/
#/*     Function Name:    security                                       */
#/*     Description:      Check to see that the client is not trying to  */
#/*                       get into an ancestor directory                 */
#/*     Parameters:       filePath - path from client                    */
#/*                       directory - user given directory               */
#/*     Return Value:     secCheck - boolean value if passed security    */
#/*                                  check                               */
#/************************************************************************/
def security(filePath, directory):
    secCheck = True

    root = normalize_path(directory)
    target = normalize_path(filePath)

    if not is_within_root(root, target):
        secCheck = False

    return secCheck

#/************************************************************************/
#/*     Function Name:    failureresponse                                */
#/*     Description:      Response to security failure                   */
#/*     Parameters:       utility - object of Utility class to send and  */
#/*                                 recieve responses and requests       */
#/*                       clientConn - client socket file descriptor     */
#/*     Return Value:     none                                           */
#/************************************************************************/
def failureResponse(utility, clientConn):
    failure = Response(status="error", message="Permission Denied")
    utility.send_all(clientConn, failure)
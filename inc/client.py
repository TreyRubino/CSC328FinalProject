#!/usr/bin/env python3

# Ian Bull

#import correct libraries
import sys
import socket
import readline
import os
import signal

from .Model.Request import Request
from .Model.Response import Response
from .Utility.Utility import Utility


class Client:
    #########################################################################
    # Function name: __init__
    # Description: Initializes the Client object with parsed command-line 
    #              arguments and a utility instance for operations.
    # Parameters: 
    #   - parsedArguments : Parsed arguments containing host and port details.
    # Return Value: None
    #########################################################################
    def __init__(self, parsedArguments): #attributes
        self.parsedArgs = parsedArguments
        self.utility = Utility()

    #########################################################################
    # Function name: shutdown_signal_handler
    # Description: Signal handler to handle shutdown in the parent process. 
    #              It raises a SystemExit exception with a message when the 
    #              server signals a shutdown.
    # Parameters: 
    #   - signum : The signal number (standard signal identifier).
    #   - frame  : The current stack frame (not used in this function).
    # Return Value: None
    #########################################################################
    def shutdown_signal_handler(self, signum, frame):
        # Signal handler to handle shutdown in the parent process
        print("Server shutdown detected. Exiting REPL...")
        raise SystemExit()  # Raise SystemExit to terminate the REPL gracefully
    
    #########################################################################
    # Function name: startClient
    # Description: Creates a socket connection to the server and starts the 
    #              REPL interface for interacting with the server.
    # Parameters: None
    # Return Value: None
    #########################################################################
    def startClient(self):
        try:
            mySock = socket.getaddrinfo(self.parsedArgs.host, self.parsedArgs.port, socket.AF_INET, socket.SOCK_STREAM)[0][4] #get ip
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #create socket
                s.connect(mySock) #connect socket       
                self.startREPL(s) #start REPL interface
        except Exception as e: #deal with errors
            print(f"Fatal Error: {e}")
            sys.exit(1)

    #########################################################################
    # Function name: startREPL
    # Description: Continuously reads user input and executes commands until 
    #              the user exits the REPL.
    # Parameters: 
    #   - s : The socket connected to the server.
    # Return Value: None
    #########################################################################
    def startREPL(self, s):
        try:
            # Set up a signal handler to catch SIGUSR1 for server shutdown
            signal.signal(signal.SIGUSR1, self.shutdown_signal_handler)

            while True:  # Loop indefinitely until exit is typed
                pid = os.fork()  # Create two processes to listen for server shutdown

                if pid == 0:  # Child process to deal with server shutdown
                    try:
                        response = self.utility.recv_all(s, Response)  # Listen for server shutdown
                        if response.status == "shutdown":  # If server shuts down
                            # Send shutdown signal to parent, but don't raise SystemExit here
                            os.kill(os.getppid(), signal.SIGUSR1)  # Send shutdown signal to parent
                            os._exit(0)  # Exit the child process gracefully
                    except Exception as e:
                        print(f"Error in child process: {e}")
                        os._exit(1)  # Ensure child exits on any exception

                elif pid > 0:  # Parent process to deal with REPL commands
                    try:
                        message = input(">>> ")  # Read user input
                        if not message.strip():
                            continue

                        # Reap the child process before restarting the loop
                        os.kill(pid, signal.SIGTERM)  # Signal the child to terminate
                        os.waitpid(pid, 0)  # Reap the child process

                        # Handle REPL commands
                        exitFound = self.executeCommand(s, message)  # Prepare and execute the correct command
                        if exitFound:  # If exit command is typed
                            break  # Exit the REPL loop

                    except Exception as e:
                        print(f"Error in parent process: {e}")
                        os.kill(pid, signal.SIGTERM)  # Signal the child to terminate
                        os.waitpid(pid, 0)  # Reap the child process
                        break

                else:  # In case of fork failure
                    print("Fork failed. Exiting REPL.")  # Inform the user
                    break  # Break out of the loop

        except KeyboardInterrupt: #in case of ctrl+C
            if pid == 0:
                response = self.utility.clear() #formatting
                request = Request(cmd="exit")
                self.exitCmd(s, request)
                print("\nExiting REPL...") #tell user 
        except EOFError:
            print("\nExiting REPL...")
        finally:
            readline.clear_history()

    #########################################################################
    # Function name: executeCommand
    # Description: Parses the user's input and executes the corresponding 
    #              command by invoking the appropriate function.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - message : The user's input command string.
    # Return Value: 
    #   - bool: True if the user inputs "exit," otherwise False.
    #########################################################################
    def executeCommand(self, s, message):
        command, *args = message.split() #split line by space

        options = [] #hold all things that start with '-'
        paths = [] #hold all different path options
        for arg in args: #for each arg
            if arg.startswith('-') and len(arg) > 1: #if an option...
                options.append(arg) #put in option list
            else: #if not an option
                paths.append(arg) #put in path list

        request = Request(command, options, *paths) #create request

        if (request.cmd.startswith('l') and request.cmd != 'ls') or request.cmd == 'put': #switch under certain contditions
            request.local_path, request.remote_path = request.remote_path, request.local_path

        #exit command
        if request.cmd == "exit": 
            self.exitCmd(s, request) #call correct function
            return True

        #clear command
        elif request.cmd == "clear":
            self.clearCmd(s, request) #call correct function

        #help command
        elif request.cmd == "help": 
            self.helpCmd(s, request) #call correct function

        #cd command
        elif request.cmd == "cd": 
            self.cdCmd(s, request) #call correct function

        #get command
        elif request.cmd == "get": 
            self.getCmd(s, request) #call correct function

        #lcd command
        elif request.cmd == "lcd": 
            self.lcdCmd(s, request) #call correct function

        #lls command
        elif request.cmd == "lls": 
            self.llsCmd(s, request) #call correct function

        #lmkdir command
        elif request.cmd == "lmkdir": 
            self.lmkdirCmd(s, request) #call correct function

        #lpwd command
        elif request.cmd == "lpwd": 
            self.lpwdCmd(s, request) #call correct function

        #ls command
        elif request.cmd == "ls": 
            self.lsCmd(s, request) #call correct function

        #mkdir command
        elif request.cmd == "mkdir": 
            self.mkdirCmd(s, request) #call correct function

        #put command
        elif request.cmd == "put": 
            self.putCmd(s, request) #call correct function

        #pwd command
        elif request.cmd == "pwd": 
            self.pwdCmd(s, request) #call correct function

        elif request.cmd == "rm":
            self.rmCmd(s, request)

        elif request.cmd == "lrm":
            self.lrmCmd(s, request)

        elif request.cmd == "cat":
            self.catCmd(s, request)

        elif request.cmd == "lcat":
            self.lcatCmd(s, request)

        else: #print error
            print(f"Command not found: {request.cmd}")
        return False #continue REPL

    #########################################################################
    # Function name: exitCmd
    # Description: Sends the "exit" command to the server, receives the 
    #              response, and disconnects from the server.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - request : The Request object containing the exit command.
    # Return Value: None
    #########################################################################
    def exitCmd(self, s, request):
        self.utility.send_all(s, request) #send command to exit
        response = self.utility.recv_all(s, Response)
        if response.status == "success":
            print("Disconnecting from server and exiting REPL.")

    #########################################################################
    # Function name: clearCmd
    # Description: Executes the "clear" command to clear the terminal screen 
    #              locally without sending a request to the server.
    # Parameters: 
    #   - s        : The socket connected to the server.
    #   - request  : The Request object containing the clear command.
    # Return Value: None
    #########################################################################
    def clearCmd(self, s, requeset):
        response = self.utility.clear() #get the response
        if response.status == "success": #if successful...
            pass #continue - no output
        else: #errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: helpCmd
    # Description: Executes the "help" command to display instructions or 
    #              available commands.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - request : The Request object containing the help command.
    # Return Value: None
    #########################################################################
    def helpCmd(self, s, request):
        response = self.utility.help() #get the response
        if response.status == "success": #if successful...
            print(response.message) #print help instructions
        else: #errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: cdCmd
    # Description: Executes the "cd" command to change the current working 
    #              directory on the server.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - request : The Request object containing the cd command.
    # Return Value: None
    #########################################################################
    def cdCmd(self, s, request):
        self.utility.send_all(s, request) #send command to change directory
        response = self.utility.recv_all(s, Response)
        if response.status == "success": #if successful...
            pass #continue - no output
        else: #errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: getCmd
    # Description: Executes the "get" command to retrieve a file from the 
    #              server.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - request : The Request object containing the get command.
    # Return Value: None
    #########################################################################
    def getCmd(self, s, request):
        response = self.utility.get(s, request)
        if response.status == "success": #if successful...
            print(response.message)
        else: #errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: lcdCmd
    # Description: Executes the "lcd" command to change the current working 
    #              directory locally on the client.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - request : The Request object containing the lcd command.
    # Return Value: None
    #########################################################################
    def lcdCmd(self, s, request):
        response = self.utility.cd(request) #get the response
        if response.status == "success": #if successful
            pass #continue - no output
        else: #errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: llsCmd
    # Description: Executes the "lls" command to list the contents of the 
    #              local directory.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - request : The Request object containing the lls command.
    # Return Value: None
    #########################################################################
    def llsCmd(self, s, request):
        response = self.utility.ls(request) #get the response
        if response.status == "success": #if successful
            print("Directory Listing:") #formatting
            if '-l' in request.options:
                for entry in response.contents:
                    print(f"{entry.mode:<10} {entry.nlink:<3} {entry.user:<8} {entry.group:<8} {entry.size:<8} {entry.mtime:<16} {entry.name}")
            else:
                for entry in response.contents:
                    print(f"{entry.name}", end = "  ")
                print("")
        else: #errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: lmkdirCmd
    # Description: Executes the "lmkdir" command to create a directory 
    #              locally on the client.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - request : The Request object containing the lmkdir command.
    # Return Value: None
    #########################################################################
    def lmkdirCmd(self, s, request):
        response = self.utility.mkdir(request) #get response
        if response.status == "success": #if successful
            pass #continue - no output
        else: #errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: lpwdCmd
    # Description: Executes the "lpwd" command to print the current working 
    #              directory locally on the client.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - request : The Request object containing the lpwd command.
    # Return Value: None
    #########################################################################
    def lpwdCmd(self, s, request):
        response = self.utility.pwd() #get response
        if response.status == "success": #if successful
            print(response.message) #print working directory
        else: #errors
            print(f"Error: {response.message}")
        
    #########################################################################
    # Function name: lsCmd
    # Description: Executes the "ls" command to list the contents of the 
    #              directory on the server.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - request : The Request object containing the ls command.
    # Return Value: None
    #########################################################################
    def lsCmd(self, s, request):
        self.utility.send_all(s, request) #send command 
        response = self.utility.recv_all(s, Response) #get response
        if response.status == "success": #if successful
            print("Directory Listing:") #formatting
            if '-l' in request.options:
                for entry in response.contents:
                    print(f"{entry.mode:<10} {entry.nlink:<3} {entry.user:<8} {entry.group:<8} {entry.size:<8} {entry.mtime:<16} {entry.name}")
            else:
                for entry in response.contents:
                    print(f"{entry.name}", end = "  ")
                print("")
        else: #errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: mkdirCmd
    # Description: Executes the "mkdir" command to create a directory on 
    #              the server.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - request : The Request object containing the mkdir command.
    # Return Value: None
    #########################################################################
    def mkdirCmd(self, s, request):
        self.utility.send_all(s, request) #send command 
        response = self.utility.recv_all(s, Response) #get response
        if response.status == "success": #if successful
            pass #continue - no output
        else: #errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: putCmd
    # Description: Executes the "put" command to send a file to the server.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - request : The Request object containing the put command.
    # Return Value: None
    #########################################################################
    def putCmd(self, s, request):
        response = self.utility.put(s, request)
        if response.status == "success": #if successful...
            print(response.message)
        else: #errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: pwdCmd
    # Description: Executes the "pwd" command to print the current working 
    #              directory on the server.
    # Parameters: 
    #   - s       : The socket connected to the server.
    #   - request : The Request object containing the pwd command.
    # Return Value: None
    #########################################################################
    def pwdCmd(self, s, request):
        self.utility.send_all(s, request) #send command 
        response = self.utility.recv_all(s, Response) #get response
        if response.status == "success": #if successful
            print(response.message) #print working directory
        else: #errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: lrmCmd
    # Description: Handles the "rm" command by invoking the utility's remove 
    #              method and checking the response status. If successful, 
    #              there is no output. In case of an error, the error message 
    #              is printed.
    # Parameters: 
    #   - s       : The socket object used for communication.
    #   - request : The request data to be sent for the "rm" operation.
    # Return Value: None
    #########################################################################
    def lrmCmd(self, s, request):
        response = self.utility.rm(request) #get the response
        if response.status == "success": #if successful
            pass #continue - no output
        else: #errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: lcatCmd
    # Description: Handles the "cat" command by invoking the utility's cat 
    #              method and checking the response status. If successful, 
    #              the response message is printed. In case of an error, the 
    #              error message is printed.
    # Parameters: 
    #   - s       : The socket object used for communication.
    #   - request : The request data to be sent for the "cat" operation.
    # Return Value: None
    #########################################################################
    def lcatCmd(self, s, request):
        response = self.utility.cat(request)  # get the response
        if response.status == "success":  # if successful
            print(response.message)
        else:  # errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: rmCmd
    # Description: Handles the "rm" command by sending a request via socket 
    #              and receiving the response. If successful, there is no 
    #              output. In case of an error, the error message is printed.
    # Parameters: 
    #   - s       : The socket object used for communication.
    #   - request : The request data to be sent for the "rm" operation.
    # Return Value: None
    #########################################################################
    def rmCmd(self, s, request):
        self.utility.send_all(s, request)  # send command
        response = self.utility.recv_all(s, Response)  # get response
        if response.status == "success":  # if successful
            pass  # continue - no output
        else:  # errors
            print(f"Error: {response.message}")

    #########################################################################
    # Function name: catCmd
    # Description: Handles the "cat" command by sending a request via socket 
    #              and receiving the response. If successful, the response 
    #              message is printed. In case of an error, the error message 
    #              is printed.
    # Parameters: 
    #   - s       : The socket object used for communication.
    #   - request : The request data to be sent for the "cat" operation.
    # Return Value: None
    #########################################################################
    def catCmd(self, s, request):
        self.utility.send_all(s, request)  # send command
        response = self.utility.recv_all(s, Response)  # get response
        if response.status == "success":  # if successful
            print(response.message)
        else:  # errors
            print(f"Error: {response.message}")

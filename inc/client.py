#!/usr/bin/env python3
#import correct libraries
import sys
import socket
import readline

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
            while True: #Loop indefinitely until exit is typed
                # Read user input
                message = input(">>> ")
                if not message.strip():
                    continue
                exitFound = self.executeCommand(s, message) #prepare and execute the correct command
                if exitFound == True: #if exit command is typed 
                    break   #break out
        except KeyboardInterrupt:
            print("\nExiting REPL...")
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
        
        elif request.cmd == "touch":
            self.touchCmd(s, request)
        
        elif request.cmd == "ltouch":
            self.ltouchCmd(s, request)

        elif request.cmd == "rm":
            self.rmCmd(s, request)

        elif request.cmd == "lrm":
            self.lrmCmd(s, request)

        elif request.cmd == "mv":
            self.mvCmd(s, request)

        elif request.cmd == "lmv":
            self.lmvCmd(s, request)

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
            print("Disconnecting from server")

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

    def lrmCmd(self, s, request):
        response = self.utility.rm(request) #get the response
        if response.status == "success": #if successful
            pass #continue - no output
        else: #errors
            print(f"Error: {response.message}")

    def ltouchCmd(self, s, request):
        response = self.utility.touch(request) #get the response
        if response.status == "success": #if successful
            pass #continue - no output
        else: #errors
            print(f"Error: {response.message}")

    def lmvCmd(self, s, request):
        response = self.utility.mv(request) #get the response
        if response.status == "success": #if successful
            pass #continue - no output
        else: #errors
            print(f"Error: {response.message}")
    
    def lcatCmd(self, s, request):
        response = self.utility.cat(request) #get the response
        if response.status == "success": #if successful
            print(response.message)
        else: #errors
            print(f"Error: {response.message}")

    def rmCmd(self, s, request):
        self.utility.send_all(s, request) #send command 
        response = self.utility.recv_all(s, Response) #get response
        if response.status == "success": #if successful
            pass #continue - no output
        else: #errors
            print(f"Error: {response.message}")
    
    def touchCmd(self, s, request):
        self.utility.send_all(s, request) #send command 
        response = self.utility.recv_all(s, Response) #get response
        if response.status == "success": #if successful
            pass #continue - no output
        else: #errors
            print(f"Error: {response.message}")

    def catCmd(self, s, request):
        self.utility.send_all(s, request) #send command 
        response = self.utility.recv_all(s, Response) #get response
        if response.status == "success": #if successful
            print(response.message)
        else: #errors
            print(f"Error: {response.message}")

    def mvCmd(self, s, request):
        self.utility.send_all(s, request) #send command 
        response = self.utility.recv_all(s, Response) #get response
        if response.status == "success": #if successful
            pass #continue - no output
        else: #errors
            print(f"Error: {response.message}")

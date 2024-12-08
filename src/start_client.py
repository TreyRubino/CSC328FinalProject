#!/usr/bin/env python3

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from inc.client import Client
from inc.Parser.clientParser import parseClient

#########################################################################
# Function name: main
# Description: The main entry point for the client application. It parses 
#              command-line arguments and initializes the Client object, 
#              then starts the client connection.
# Parameters: None
# Return Value: None
#########################################################################
def main():
    parsedArgs = parseClient(sys.argv[1:]) #get command line values
    
    client1 = Client(parsedArgs)
    client1.startClient()

if __name__ == "__main__":
    main() #call the main function
#!/usr/bin/env python3
import argparse

#########################################################################
# Function name: parseClient
# Description: Parses command-line arguments for a client application. 
#              The arguments include the host and port details.
# Parameters: 
#   - args : List of command-line arguments to parse.
# Return Value: 
#   - parsedArgs : An object containing the parsed host and port values.
#########################################################################
def parseClient(args):
    # Disable the default help flag to make sure it doesnt freak out
    parser = argparse.ArgumentParser(description="Process some command line arguments.", add_help=False)
    
    # Add arguments
    parser.add_argument('-h', '--host', type=str, required=True, help='Host name')
    parser.add_argument('-p', '--port', type=str, required=True, help='Port number')

    # Parse the arguments from the provided list
    parsedArgs = parser.parse_args(args)

    # Return the values 
    return parsedArgs
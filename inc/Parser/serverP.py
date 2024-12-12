#!/usr/bin/env python3

# Alexa Fisher

import argparse
import sys
import os

#Citation:
# Author: Dr. Schwesinger
# Source: public examples
# Retrieved November 26th, 2024

#/************************************************************************/
#/*     Function Name:    parse                                          */
#/*     Description:      Parses together the command line arguments for */
#/*                       later use.                                     */
#/*     Parameters:       argv - command line arguments                  */
#/*     Return Value:     tuple of port number, directory, and absolute  */
#/*                       path of the directory given                    */
#/************************************************************************/
def parseArgs(argv):
    '''
    Description: parse command line arguments
    Return: named tuple of the argument values
    '''

    parser = argparse.ArgumentParser(description='Get command line arguments')
    parser.add_argument('-p', required=True, help='Port Number')
    parser.add_argument('-d', required=True, help='Directory')

    try:
        args = parser.parse_args(argv) #parse the arguments
        port, directory = args.p, args.d #set variables to arguments
        absDir = os.path.abspath(directory)
    except SystemExit:
        sys.exit(1) #failure to parse correctly

    return port, directory, absDir #return the variables
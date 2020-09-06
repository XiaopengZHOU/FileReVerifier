#!/usr/bin/python

from enum import Enum
class InputStyle(Enum):
    Default = 0
    Legacy = 1

def get_parameters():
    pass

def main():
    input_file = None
    input_style = InputStyle.Default
    work_directory = None

    from getopt import error
    try:
        from getopt import getopt
        from sys import argv

        opts, argv = getopt(argv[1:], "i:s:w:")
        for k, v in opts:
            if "-i" == k:
                from os.path import isfile
                if not isfile(v):
                    show_usage()

                    print("Input file not found for option \"-i '%s'\"" % v)

                    exit(2)
                else:
                    input_file = v

            elif "-s" == k:
                if "legacy" == v.lower():
                    input_style = InputStyle.Legacy
                elif "default" == v.lower():
                    input_style = InputStyle.Default
                else:
                    show_usage()

                    print("Unknown input style \"%s\"" % v)

                    exit(2)

            elif "-w" == k:
                from os.path import isdir
                if not isdir(v):
                    show_usage()

                    print("Directory not found for option \"-w '%s'\"" % v)

                    exit(2)
                else:
                    work_directory = v

    except error as msg:
        show_usage()

        from sys import stdout, stderr
        stdout = stderr
        print(msg)

        exit(1)

    if input_file is None:
        show_usage()

        print("Please specifiy an input file")

        exit(3)

    if work_directory is None:
        from os import getcwd
        work_directory = getcwd()

    #print("WorkDirectory: \"%s\"" % work_directory)

def reverify_file

def show_usage():
    print("Usage: ./file_reverifier.py -i <input-file> -s <default | legacy> "
        "-w <work-dir>\n")

if __name__ == "__main__":
    main()

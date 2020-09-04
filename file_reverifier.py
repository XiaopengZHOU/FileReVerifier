#!/usr/bin/python

from enum import Enum
class InputStyle(Enum):
    Default = 0
    Legacy = 1

def main():
    input_style = InputStyle.Default
    work_directory = None

    from getopt import error
    try:
        from getopt import getopt
        from sys import argv

        opts, argv = getopt(argv[1:], "s:w:")
        for k, v in opts:
            if "-s" == k:
                if "legacy" == v.lower():
                    input_style = InputStyle.Legacy
                elif "default" == v.lower():
                    input_style = InputStyle.Default
                else:
                    show_usage()

                    print("Unknown output style \"%s\"" % v)

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

    if work_directory is None:
        from os import getcwd
        work_directory = getcwd()

    #print("WorkDirectory: \"%s\"" % work_directory)

def show_usage():
    print("Usage: ./file_reverifier.py -s <default | legacy> -w <work-dir>\n")

if __name__ == "__main__":
    main()

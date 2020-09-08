#!/usr/bin/python

from enum import Enum
class InputStyle(Enum):
    Default = 0
    Legacy = 1

def get_parameters():
    input_file_name = None
    input_file_style = InputStyle.Default
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

                    return 2, input_file_name, input_file_style, \
                        work_directory
                else:
                    input_file_name = v

            elif "-s" == k:
                if "legacy" == v.lower():
                    input_file_style = InputStyle.Legacy
                elif "default" == v.lower():
                    input_file_style = InputStyle.Default
                else:
                    show_usage()

                    print("Unknown input style \"%s\"" % v)

                    return 2, input_file_name, input_file_style, \
                        work_directory

            elif "-w" == k:
                from os.path import isdir
                if not isdir(v):
                    show_usage()

                    print("Directory not found for option \"-w '%s'\"" % v)

                    return 2, input_file_name, input_file_style, \
                        work_directory
                else:
                    work_directory = v

    except error as msg:
        show_usage()

        from sys import stdout, stderr
        stdout = stderr
        print(msg)

        return 1, input_file_name, input_file_style, work_directory

    if input_file_name is None:
        show_usage()

        print("Please specifiy an input file")

        return 3, input_file_name, input_file_style, work_directory

    if work_directory is None:
        from os import getcwd
        work_directory = getcwd()

    return 0, input_file_name, input_file_style, work_directory

def main():
    ret, input_file_name, input_file_style, work_directory = get_parameters()

    if 0 != ret:
        exit(ret)

    #print("InputFile: \"%s\"" % input_file_name)
    #print("WorkDirectory: \"%s\"" % work_directory)

    reverify_file(input_file_name = input_file_name,
        input_file_style = input_file_style, work_directory = work_directory)

def reverify_file(input_file_name, input_file_style, work_directory):
    input_file = open(input_file_name, "r")
    lines = input_file.readlines()

    #count = 0
    #for line in lines:
    #    print("Line {}: {}".format(count, line.strip()))
    #    count += 1



def show_usage():
    print("Usage: ./file_reverifier.py -i <input-file> "
        "-s <default | legacy> -w <work-dir>\n")

if __name__ == "__main__":
    main()

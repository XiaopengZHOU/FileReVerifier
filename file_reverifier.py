#!/usr/bin/python

from enum import Enum
class InputFileStyle(Enum):
    Default = 0
    Legacy = 1

def main():
    from sys import argv
    ret, input_file_name, input_file_style, work_directory = \
        parse_command_line_options(argv)
    if 0 != ret:
        exit(ret)

    #print("InputFile: \"%s\"" % input_file_name)
    #print("WorkDirectory: \"%s\"" % work_directory)

    reverify_file(input_file_name = input_file_name,
        input_file_style = input_file_style, work_directory = work_directory)

def parse_command_line_options(arg_vector):
    input_file_name = None
    input_file_style = InputFileStyle.Default
    work_directory = None

    from getopt import error
    try:
        from getopt import getopt
        opts, argv = getopt(arg_vector[1:], "i:s:w:")
        for k, v in opts:
            if "-i" == k:
                from os.path import isfile
                if not isfile(v):
                    show_usage()

                    from sys import stderr
                    print("Input file not found for option \"-i '%s'\"" % v,
                        file=stderr)

                    return 2, input_file_name, input_file_style, \
                        work_directory
                else:
                    input_file_name = v
            elif "-s" == k:
                if "legacy" == v.lower():
                    input_file_style = InputFileStyle.Legacy
                elif "default" == v.lower():
                    input_file_style = InputFileStyle.Default
                else:
                    show_usage()

                    from sys import stderr
                    print("Unknown input file style \"%s\"" % v, file=stderr)

                    return 2, input_file_name, input_file_style, \
                        work_directory
            elif "-w" == k:
                from os.path import isdir
                if not isdir(v):
                    show_usage()

                    from sys import stderr
                    print("Directory not found for option \"-w '%s'\"" % v,
                        file=stderr)

                    return 2, input_file_name, input_file_style, \
                        work_directory
                else:
                    work_directory = v

    except error as msg:
        show_usage()

        from sys import stderr
        print(msg, file=stderr)

        return 1, input_file_name, input_file_style, work_directory

    if input_file_name is None:
        show_usage()

        from sys import stderr
        print("Please specifiy an input file", file=stderr)

        return 3, input_file_name, input_file_style, work_directory

    if work_directory is None:
        from os import getcwd
        work_directory = getcwd()

    return 0, input_file_name, input_file_style, work_directory

def reverify_file(input_file_name, input_file_style, work_directory):
    import sqlite3
    try:
        db = sqlite3.connect(":memory:")

        cur = db.cursor()

        statement = (
                "CREATE TABLE temp ("
                        "idx INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "filename TEXT NOT NULL, "
                        "fullpath TEXT DEFAULT \"\", "
                        "checksum TEXT NOT NULL, "
                        "checked INTEGER DEFAULT 0, "
                        "updated INTEGER DEFAULT 0, "
                        "added INTEGER DEFAULT 0"
                    ");"
            )
        cur.execute(statement)

        if InputFileStyle.Legacy == input_file_style:
            input_file = open(input_file_name, "r", encoding="iso-8859-1")
        else:
            input_file = open(input_file_name, "r")
        lines = input_file.readlines()

        #count = 0
        for line in lines:
            line = line.strip()
            separator_pos = line.rfind(" ")
            target_file_name = line[:separator_pos].strip()
            target_file_checksum = line[separator_pos + 1:].strip()
            #print("Line {}: {} {}".format(count, target_file_name, \
            #    target_file_checksum))
            #count += 1

            statement = (
                    "INSERT INTO temp (filename, checksum) VALUES "
                            "(\"" + target_file_name + "\", "
                            "\"" + target_file_checksum + "\""
                        ");"
                )
            #print(statement)
            cur.execute(statement)

        cur.execute("SELECT count(*) FROM temp;")
        rows = cur.fetchall()
        print("%s file(s) found in input file." % rows[0][0])

        verify_files(current_directory = work_directory, cur = cur)

        cur.execute("SELECT count(*) FROM temp WHERE checked=1;")
        rows = cur.fetchall()
        print("%s file(s) checked." % rows[0][0])

        create_new_file = False

        cur.execute("SELECT count(*) FROM temp WHERE checked=0;")
        rows = cur.fetchall()
        print("%s file(s) unchecked." % rows[0][0])
        if (0 != rows[0][0]):
            create_new_file = True
            cur.execute("SELECT filename, checksum FROM temp WHERE "
                "checked=0;")
            rows = cur.fetchall()
            for row in rows:
                print("Filename=\"%s\" Checksum=%s" %
                    (row[0], row[1]))

        cur.execute("SELECT count(*) FROM temp WHERE updated=1;")
        rows = cur.fetchall()
        print("%s file(s) updated." % rows[0][0])
        if (0 != rows[0][0]):
            create_new_file = True
            cur.execute("SELECT fullpath, checksum FROM temp "
                "WHERE updated=1;")
            rows = cur.fetchall()
            for row in rows:
                print("FullPath=\"%s\" Checksum=%s" %
                    (row[0], row[1]))

        cur.execute("SELECT count(*) FROM temp WHERE added=1;")
        rows = cur.fetchall()
        print("%s file(s) added." % rows[0][0])
        if (0 != rows[0][0]):
            create_new_file = True
            cur.execute("SELECT fullpath, checksum FROM temp WHERE added=1;")
            rows = cur.fetchall()
            for row in rows:
                print("FullPath=\"%s\" Checksum=%s" %
                    (row[0], row[1]))

        if create_new_file:
            print("new file")
            with open('/tmp/file_reverifier.txt', 'w') as fh:
                cur.execute("SELECT filename, checksum FROM temp "
                    "WHERE checked=1;")
                rows = cur.fetchall()
                from os import linesep
                for row in rows:
                    fh.write(row[0] + " " + row[1] + linesep)
                    #print("filename=\"%s\" checksum=%s" % (row[0], row[1]))

    finally:
        if db:
            db.close()

def sum_from_file_CRC32(filename):
    from zlib import crc32
    with open(filename, "rb") as fh:
        hash = 0
        while True:
            s = fh.read(65536)
            if not s:
                break
            hash = crc32(s, hash)

        return "%08X" % (hash & 0xFFFFFFFF)

def show_usage():
    print("Usage: ./file_reverifier.py -i <input-file> -s <default | legacy> "
        "-w <work-dir>\n")

def verify_file(target_file_name, fullpath, checksum, cur):
    statement = (
            "SELECT idx FROM temp WHERE "
                "filename=\"" + target_file_name + "\" AND "
                "checksum=\"" + checksum + "\" AND "
                "checked=0;"
        )
    #print(statement)
    cur.execute(statement)
    rows = cur.fetchall()
    if rows:
        #print("idx=%s" % rows[0][0])

        statement = (
                "UPDATE temp "
                    "SET checked=1, "
                        "fullpath=\"" + fullpath + "\" "
                    "WHERE idx=" + str(rows[0][0]) + ";"
            )
        #print(statement)
        cur.execute(statement)

        print("\"%s\" ok" % target_file_name)
    else:
        statement = (
                "SELECT idx FROM temp WHERE "
                    "checksum=\"" + checksum + "\" AND "
                    "checked=0;"
            )
        #print(statement)
        cur.execute(statement)
        rows = cur.fetchall()

        if rows:
            #print("idx=%s" % rows[0])

            statement = (
                    "UPDATE temp "
                        "SET checked=1, updated=1, "
                            "filename=\"" + target_file_name + "\", "
                            "fullpath=\"" + fullpath + "\" "
                        "WHERE idx=" + str(rows[0][0]) + ";"
                )
            #print(statement)
            cur.execute(statement)

            print("\"%s\" updated" % target_file_name)
        else:
            statement = (
                    "INSERT INTO temp (filename, fullpath, checksum, added, "
                                "checked) VALUES ("
                            "\"" + target_file_name + "\", "
                            "\"" + fullpath + "\", "
                            "\"" + checksum + "\", "
                            "1, "
                            "1"
                        ");"
                )
            #print(statement)
            cur.execute(statement)

            print("No match found: filename=\"%s\" checksum=%s" %
                (target_file_name, checksum))

def verify_files(current_directory, cur):
    #print(current_directory)
    from os import listdir
    items = listdir(current_directory)

    for item in items:
        if not item.startswith("."):
            from os.path import join
            fullpath = join(current_directory, item)

             #print("FullPath: \"%s\"" % fullpath)

            from os import stat
            st_mode = stat(fullpath).st_mode

            from stat import S_ISDIR, S_ISLNK, S_ISREG
            if S_ISLNK(st_mode):
                pass
            elif S_ISDIR(st_mode):
                verify_files(current_directory = fullpath, cur = cur)
            elif S_ISREG(st_mode):
                #print("%s 0x%s" % (item, sum_from_file_CRC32(fullpath)))
                verify_file(target_file_name = item, fullpath = fullpath,
                     checksum = "0x" + sum_from_file_CRC32(fullpath),
                     cur = cur)

if __name__ == "__main__":
    main()

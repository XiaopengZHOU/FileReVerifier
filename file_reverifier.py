#!/usr/bin/python

def get_parameters():
    input_file_name = None
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

                    return 2, input_file_name, work_directory
                else:
                    input_file_name = v
            elif "-w" == k:
                from os.path import isdir
                if not isdir(v):
                    show_usage()

                    print("Directory not found for option \"-w '%s'\"" % v)

                    return 2, input_file_name, work_directory
                else:
                    work_directory = v

    except error as msg:
        show_usage()

        from sys import stdout, stderr
        stdout = stderr
        print(msg)

        return 1, input_file_name, work_directory

    if input_file_name is None:
        show_usage()

        print("Please specifiy an input file")

        return 3, input_file_name, work_directory

    if work_directory is None:
        from os import getcwd
        work_directory = getcwd()

    return 0, input_file_name, work_directory

def main():
    ret, input_file_name, work_directory = get_parameters()

    if 0 != ret:
        exit(ret)

    #print("InputFile: \"%s\"" % input_file_name)
    #print("WorkDirectory: \"%s\"" % work_directory)

    reverify_file(input_file_name = input_file_name,
        work_directory = work_directory)

def reverify_file(input_file_name, work_directory):
    import sqlite3
    try:
        db = sqlite3.connect(":memory:")

        cur = db.cursor()

        statement = (
                "CREATE TABLE temp ("
                        "idx INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "filename TEXT NOT NULL, "
                        "checksum TEXT NOT NULL, "
                        "checked INTEGER DEFAULT 0, "
                        "updated INTEGER DEFAULT 0, "
                        "added INTEGER DEFAULT 0"
                    ");"
            )
        cur.execute(statement)

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
        row = cur.fetchall()
        print("%s file(s) found in input file." % row[0][0])

        verify_files(current_directory = work_directory, cur = cur)

        cur.execute("SELECT count(*) FROM temp WHERE checked=1;")
        row = cur.fetchall()
        print("%s file(s) checked." % row[0][0])

        cur.execute("SELECT count(*) FROM temp WHERE checked=0;")
        row = cur.fetchall()
        print("%s file(s) unchecked." % row[0][0])

        cur.execute("SELECT count(*) FROM temp WHERE updated=1;")
        row = cur.fetchall()
        print("%s file(s) updated." % row[0][0])

        cur.execute("SELECT count(*) FROM temp WHERE added=1;")
        row = cur.fetchall()
        print("%s file(s) added." % row[0][0])

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
    print("Usage: ./file_reverifier.py -i <input-file> "
        "-s <default | legacy> -w <work-dir>\n")

def verify_file(target_file_name, checksum, cur):
    statement = (
            "SELECT idx FROM temp WHERE "
                "filename=\"" + target_file_name + "\" AND "
                "checksum=\"" + checksum + "\" AND "
                "checked=0;"
        )
    #print(statement)
    cur.execute(statement)
    row = cur.fetchall()

    if row is not None:
        #print("idx=%s" % row[0])

        statement = (
                "UPDATE temp "
                    "SET checked=1 "
                    "WHERE idx=" + str(row[0][0]) + ";"
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
        row = cur.fetchall()

        if row is not None:
            #print("idx=%s" % row[0])

            statement = (
                    "UPDATE temp "
                        "SET checked=1, updated=1, "
                            "filename=\"" + target_file_name + "\" "
                        "WHERE idx=" + str(row[0][0]) + ";"
                )
            #print(statement)
            cur.execute(statement)

            print("\"%s\" updated" % target_file_name)
        else:
            print("No match found: filename=\"%s\" checksum=%s" %
                (target_file_name, checksum))

            statement = (
                    "INSERT INTO temp (filename, checksum, added, checked) VALUES ("
                            "\"" + target_file_name + "\", "
                            "\"" + checksum + "\", "
                            "1, "
                            "1"
                        ");"
                )
            #print(statement)
            cur.execute(statement)

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
                verify_file(item, "0x" + sum_from_file_CRC32(fullpath), cur)

if __name__ == "__main__":
    main()

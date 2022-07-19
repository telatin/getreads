#!/usr/bin/env python

import argparse
import os
import sys

def isEmpty(path):
    if os.path.isfile(path):
        return os.stat(path,  follow_symlinks=True).st_size == 0
    else:
        return False

 
def remove(file, dry=False):
    if dry:
        print("DRY-RUN removing: " + file, file=sys.stderr)
        return False
    else:
        print("Removing: " + file, file=sys.stderr)
        try:
            os.remove(file)
            return True
        except OSError:
            print("Error removing: " + file, file=sys.stderr)
            return False
args = argparse.ArgumentParser()
args.add_argument("FILES", help="List of files", nargs="*")
args.add_argument("-s", "--string", help="Also remove files containing this string in the specified directory")
args.add_argument("-d", "--dir", help="Directory to search for files to remove [default: current directory]", default=".")

args.add_argument("-u", "--dry", help="Dry-run", action="store_true")

args.add_argument("--verbose", help="Verbose output", action="store_true")
args = args.parse_args()

checked_files = []
empty_files = []
removed_files = []
if args.verbose:
    print("[1] Checking %s files" % len(args.FILES), file=sys.stderr)

for file in args.FILES:
    checked_files.append(file)
    if isEmpty(file):
        if remove(file, args.dry):
            removed_files.append(file)
        empty_files.append(file)


if args.string is not None:
    if args.verbose:
        print("[2] Checking files in %s containing \"%s\"" % (args.dir, args.string), file=sys.stderr)

    for root, dirs, files in os.walk(args.dir):
        for file in files:
            if args.string in file:
                checked_files.append(os.path.join(root, file))
                if isEmpty(os.path.join(root, file)):
                    if remove(os.path.join(root, file), args.dry):
                        removed_files.append(os.path.join(root, file))
                    empty_files.append(os.path.join(root, file))

print("%s files checked, %s empty, %s removed" % (len(checked_files), len(empty_files), len(removed_files)), file=sys.stderr)
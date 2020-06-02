# -*- coding: utf-8 -*-

__version__ = "0.0.0"


import sys
import os
import json
from plgspl.to_pdf import to_pdf
from plgspl.classlist import classlist
from plgspl.merge import merge


def append_cwd(s):
    return os.path.join(os.getcwd(), s)


def validate_files(l):
    for f in l:
        if not os.path.isfile(f):
            print("Unable to find the given file: %s" % f)
            sys.exit(1)


def main():
    print("Running plgspl version %s..." % __version__)
    print("List of argument strings: %s" % sys.argv[1:])
    cmd = sys.argv[1]
    if cmd == 'pdf':
        args = list(map(append_cwd, sys.argv[2:]))
        validate_files(args[0:1])
        file_dir = args[2] if len(args) == 3 else None
        if file_dir and not os.path.isdir(file_dir):
            print("Unable to find the given file directory: %s" % f)
            sys.exit(1)
        to_pdf(args[0], args[1], file_dir)
    elif cmd == "classlist":
        f = sys.argv[2]
        validate_files([f])
        classlist(f)
    elif cmd == "merge":
        args = sys.argv[2:]
        validate_files(args[0:2])
        instance = 1
        if len(args) > 2 :
            instance = int(args[2])
        merge(args[0], args[1], instance)

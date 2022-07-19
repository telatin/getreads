#!/usr/bin/env python

import argparse
import os
import sys

args = argparse.ArgumentParser()
args.add_argument("FILES", help="List of files", nargs="*")
args.add_argument("-s", "--string", help="Remove files containing this string")
args = args.parse_args()
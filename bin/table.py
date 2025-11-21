#!/usr/bin/env python3
"""
Read ffq JSON sample info and print it as a TSV table.
"""

import argparse
import json
import sys

def safe_str(val):
    """Ensure value is a string without tabs."""
    if val is None:
        return ""
    s = str(val)
    return s.replace("\t", " ")

def main():
    parser = argparse.ArgumentParser(prog="table")
    parser.add_argument("FILES", nargs="+", help="ffq JSON files")
    args = parser.parse_args()
    print("Reading JSON files: %s" % args.FILES, file=sys.stderr)

    keys = ["accession", "experiment", "study", "sample", "title"]
    print("\t".join(keys))

    for filename in args.FILES:
        with open(filename, "r") as f:
            data = json.load(f)
            print(" Read JSON file: %s" % filename, file=sys.stderr)

        for sample_id, sample_data in data.items():
            print("     Sample ID: %s" % sample_id, file=sys.stderr)
            row = []
            for key in keys:
                value = sample_data.get(key, "")
                row.append(safe_str(value))
            print("\t".join(row))

if __name__ == "__main__":
    main()

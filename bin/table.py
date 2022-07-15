#!/usr/bin/env python
"""
Check statistics and number of samples downloaded
"""

import argparse
import os, sys, json
 
if __name__ == "__main__":
    args = argparse.ArgumentParser(prog="check-stats")
    args.add_argument("FILES", help="ffq JSON files", nargs="+")
    args = args.parse_args()
    
    keys = ["accession", "experiment", "study", "sample", "title"]
    print("\t".join(keys))
    for file in args.FILES:
        with open(file, "r") as f:
            data = json.load(f)
            for sample in data:
                line = []
                for h in keys:
                    if h in data[sample]:
                        val = data[sample][h] if not "\t" in data[sample][h] else  data[sample][h].replace("\t", " ")
                        line.append(val)
                    else:
                        line.append("")
                
                print("\t".join(line))

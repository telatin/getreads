#!/usr/bin/env python
"""
Check statistics and number of samples downloaded
"""

import argparse
import subprocess, sys


def check_sra(bin="fasterq-dump"):
    """
    Check if ffq is installed.
    """
    try:
        subprocess.check_output([bin, "-h"])
        return True
    except:
        return False


def loadstats(file):
    stats = {}
    try:
        with open(file, "r") as f:
            for line in f:
                if line.startswith("File\t#Seq\t"):
                    continue
                fields = line.strip().split("\t")
                stats[fields[0]] = fields[1:]
        
        return stats
    except Exception as e:
        # We check here and exit, no need to return errors to main
        print("ERROR: Unable to reads stats '%s':\n %s" % (file, e), file=sys.stderr)
        exit(0)

def loadfile(file):
    lines = []
    try:
        with open(file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or len(line) < 1:
                    continue
                
                lines.append(line)
        
        return lines
    except Exception as e:
        # We check here and exit, no need to return errors to main
        print("ERROR: Unable to reads IDs list '%s':\n %s" % (file, e), file=sys.stderr)
        exit(0)


def tryFasterDump(id, outdir, threads=1, verbose=False):
    cmd = ["fasterq-dump", "--threads", str(threads), "-o", outdir, id]
    if verbose:
        print("[INFO] Running fasterdump: %s" % (" ".join(cmd)), file=sys.stderr)
    
    fasterProc = subprocess.Popen(cmd, stderr = subprocess.PIPE) 
    try:
        outs, errs = fasterProc.communicate(timeout=2*60*60) # will raise error and kill any process that runs longer than 60 seconds
    except subprocess.TimeoutExpired as e:
        fasterProc.kill()
        outs, errs = fasterProc.communicate()
        print("[STDOUT] %s" % outs, file=sys.stderr)
        print("[STDERR] %s" % errs, file=sys.stderr)
        print("[ERROR] Timeout for fasterdump: %s" % (e), file=sys.stderr)
        return False



if __name__ == "__main__":
    args = argparse.ArgumentParser(prog="check-stats")
    args.add_argument("--stats", help="SeqFu stats file", required=True)
    args.add_argument("--list", help="Initial list file")
    args.add_argument("--threads", help="Number of threads", type=int, default=1)
    
    args.add_argument("--fail", help="Fail if missing files", action="store_true")
    args.add_argument("--rescue", help="Rescue if missing files", action="store_true")
    args.add_argument("--verbose", help="Verbose mode", action="store_true")
    
    args = args.parse_args()
    
    stats = loadstats(args.stats)

    has_sra = check_sra()
    if args.verbose:
        print("[INFO] SRA toolkit found: %s" % (has_sra), file=sys.stderr)

    if args.list:
        ids = loadfile(args.list)
        files_per_id = {}
        missing_ids = []
        bad_counts_ids = []
        for id in ids:
            for readfile in stats:
                if id in readfile:
                    if id in files_per_id:
                        files_per_id[id].append(readfile)
                    else:
                        files_per_id[id] = [readfile]
        for id in ids:
            if id in files_per_id:
                counts = -1
                for file in files_per_id[id]:
                    if counts == -1:
                        counts = stats[file][0]
                    elif counts != stats[file][0]:
                        print("File %s has %i reads, expected %i" % (file, stats[file][0], counts), file=sys.stderr)
                        bad_counts_ids.append(id)
                if not id in bad_counts_ids:
                    print(id, "\t", len(files_per_id[id]), "files", sep="")
                else:
                    print(id, "\t", len(files_per_id[id]), "files\tUNEVEN", sep="")

            else:
                if has_sra and tryFasterDump(id, ".", threads=args.threads, verbose=args.verbose):
                    print(id, "\t", "? files\tRESCUED", sep="")
                else:
                    print(id, "\t0 files\t(NOT FOUND)", sep="")
                    missing_ids.append(id)

        if len(missing_ids)>0 or len(bad_counts_ids)>0:
            if len(bad_counts_ids)>0:
                print("WARNING: uneven counts from files for IDs: ", ",".join(bad_counts_ids), file=sys.stderr)
            if len(missing_ids)>0:
                print("ERROR: missing IDs in stats: ", ",".join(missing_ids), file=sys.stderr)
                if args.fail:
                    exit(1)
                
            
        
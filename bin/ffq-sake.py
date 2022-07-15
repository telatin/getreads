#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run the ffq command and catch errors:
 * ERROR 400 Client Error (unrecoverable: abort)
 * 429 (too many requests: try again)
"""

from socket import timeout
import sys, os
import subprocess
import time
import json
import argparse

def check_ffq(bin="ffq"):
    """
    Check if ffq is installed.
    """
    try:
        subprocess.check_output([bin, "--help"])
        return True
    except:
        return False

def ffq(sample, outfile, bin):
    """
    return Success, Retry
    """
    cmd = [bin, "-o", outfile, sample]
    try:
        pipes = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = pipes.communicate()
        stderr = stderr.decode("utf-8")
        if pipes.returncode != 0:
            if "ERROR 400" in stderr:
                print("[ERROR] Error 400: for %s (unrecoverable: abort)" % sample, file=sys.stderr)
                return False, False
            elif "429" in stderr:
                print("[ERROR] 429: for %s (try again)" % sample, file=sys.stderr)
                return False, True
            else:
                print("[ERROR] Unknown error for %s" % sample, file=sys.stderr)
                return False
        else:
            return True, False
    except Exception as e:
        print("Error running 'ffq': %s" % e, file=sys.stderr)
        return False, False


def tryFFQ(id, outdir, retry_times=3, pause=2.0, verbose=False, bin="ffq"):
    outfile = os.path.join(outdir, "%s.json" % id)
    for attempt_number in range(retry_times):

        time.sleep(pause * attempt_number)
        if verbose:
            print("  [INFO] Running ffq #%s/%s: %s" % (attempt_number + 1,  retry_times, " ".join([bin, id, "-o", outfile])), file=sys.stderr)
        success, retry = ffq(id, outfile, bin)
        if success:
            return attempt_number + 1
        elif not retry:
            if verbose:
                print("  [ERROR] unrecoverable ffq error %s" % id, file=sys.stderr)
    
    if verbose:
        print("  [ERROR] Failed to run ffq for %s" % id, file=sys.stderr)
    return -1

def tryFasterDump(id, outdir, threads=1, verbose=False):
    cmd = ["fasterq-dump", "--threads", str(threads), "-o", outdir, id]
    if verbose:
        print("[INFO] Running fasterdump: %s" % (" ".join(cmd)), file=sys.stderr)
    
    try:
        pipes = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=100*60)
        _, stderr = pipes.communicate()
        stderr = stderr.decode("utf-8")
        if pipes.returncode != 0:
            print("[ERROR] Error running fasterdump: %s" % stderr, file=sys.stderr)
            return False
        else:
            return True
    except Exception as e:
        print("Error running 'fasterdump': %s" % e, file=sys.stderr)
        return False

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("IDs", help="Accession ID(s)", nargs="+")
    args.add_argument("-o", "--output-dir", help="Output directory [default: %(default)s]", default=".")
    args.add_argument("-r", "--retry", type=int, help="Retry up to INT times [default: %(default)s", default=4)
    args.add_argument("-p", "--pause-after", type=float, help="Pause for attempt * INT seconds [default: %(default)s", default=10.0)

    args.add_argument("-t", "--threads", type=int, help="Number of threads [default: %(default)s]", default=1)
    args.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    args = args.parse_args()

    if not check_ffq():
        print("ERROR: ffq is not installed.")
        sys.exit(1)
    
    samples_status = {}
    json_files = {}
    
    for ID in args.IDs:
        if args.verbose:
            print("--------------------- \n[INFO] Trying %s" % ID, file=sys.stderr)

        # Try "ffq" upt to retry times
        attempt = tryFFQ(ID, args.output_dir, args.retry, args.pause_after, args.verbose)

        if attempt >= 0:
            if args.verbose:
                print("[INFO] Success %s (attempt=%s)" % (ID, attempt), file=sys.stderr)
            samples_status[ID] = "success, ffq (%s)" % attempt
        else:
            if args.verbose:
                print("[INFO] Failed %s" % ID, file=sys.stderr)
            samples_status[ID] = "failed"

        #else:
        #    if args.verbose:
        #        print("[INFO] ffq failed, trying fasterdump", file=sys.stderr)
        #    fasterStatus = tryFasterDump(ID, args.output_dir, args.threads, args.verbose)

        #    if fasterStatus:
        #        samples_status[ID] = "success, fasterdump"
        #        print("%s OK" % ID)
        #    else:
        #        samples_status[ID] = "failed"
    
    for sample in samples_status:
        print("%s: %s" % (sample, samples_status[sample]))
            

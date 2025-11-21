#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run the ffq command and catch errors:
 * ERROR 400 Client Error (unrecoverable: abort)
 * 429 (too many requests: try again)

Adds verbose debug output with -v / --verbose.
"""

import sys
import os
import subprocess
import time
import json
import argparse


def debug(msg, verbose=False):
    """Print debug/info messages to stderr if verbose is enabled."""
    if verbose:
        print(msg, file=sys.stderr)


def check_ffq(ffq_bin="ffq", verbose=False):
    """
    Check if ffq is installed and callable.
    """
    try:
        debug(f"[DEBUG] Checking ffq binary: {ffq_bin}", verbose)
        subprocess.check_output([ffq_bin, "--help"], stderr=subprocess.STDOUT)
        debug("[DEBUG] ffq is available.", verbose)
        return True
    except subprocess.CalledProcessError as e:
        debug(f"[ERROR] ffq --help returned non-zero exit code: {e}", verbose)
        return False
    except FileNotFoundError:
        debug(f"[ERROR] ffq binary not found: {ffq_bin}", verbose)
        return False
    except Exception as e:
        debug(f"[ERROR] Unexpected error while checking ffq: {e}", verbose)
        return False


def ffq(sample, outfile, ffq_bin="ffq", verbose=False):
    """
    Run ffq for a single sample.

    Returns:
        (success: bool, retry: bool)
    """
    cmd = [ffq_bin, "-o", outfile, sample]
    debug(f"[DEBUG] Running command: {' '.join(cmd)}", verbose)
    try:
        pipes = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = pipes.communicate()
        stderr = stderr.decode("utf-8", errors="replace")
        stdout = stdout.decode("utf-8", errors="replace")

        debug(f"[DEBUG] Return code: {pipes.returncode}", verbose)
        if stdout.strip():
            debug(f"[DEBUG] STDOUT:\n{stdout}", verbose)
        if stderr.strip():
            debug(f"[DEBUG] STDERR:\n{stderr}", verbose)

        if pipes.returncode != 0:
            if "ERROR 400" in stderr:
                print(
                    f"[ERROR] Error 400 for {sample} "
                    "(success=False, retry=False: unrecoverable: abort)",
                    file=sys.stderr,
                )
                return False, False
            elif "429" in stderr:
                print(
                    f"[ERROR] 429 Too Many Requests for {sample} "
                    "(success=False, retry=True: will try again)",
                    file=sys.stderr,
                )
                return False, True
            else:
                print(
                    f"[ERROR] Unknown ffq error for {sample} "
                    "(success=False, retry=False)",
                    file=sys.stderr,
                )
                return False, False
        else:
            return True, False

    except Exception as e:
        print(f"[ERROR] Exception while running ffq for {sample}: {e}", file=sys.stderr)
        return False, False


def load_json(outfile, sample, verbose=False):
    """
    Load JSON from outfile and ensure the sample key is present.

    Returns:
        attempts_ok (bool)
    """
    debug(f"[DEBUG] Loading JSON from {outfile}", verbose)
    if not os.path.exists(outfile):
        print(f"[ERROR] Expected JSON file not found for {sample}: {outfile}", file=sys.stderr)
        return False

    try:
        with open(outfile, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as e:
        print(
            f"[ERROR] Invalid JSON for {sample} in {outfile}: {e}",
            file=sys.stderr,
        )
        return False
    except Exception as e:
        print(
            f"[ERROR] Could not read JSON for {sample} from {outfile}: {e}",
            file=sys.stderr,
        )
        return False

    if sample not in data:
        print(
            f"[ERROR] JSON for {sample} does not contain expected key '{sample}'",
            file=sys.stderr,
        )
        debug(f"[DEBUG] JSON keys: {list(data.keys())}", verbose)
        return False

    debug(f"[DEBUG] JSON for {sample} loaded successfully.", verbose)
    return True


def tryFFQ(sample_id, outdir, retry_times=3, pause=2.0, verbose=False, ffq_bin="ffq"):
    """
    Try running ffq multiple times for a given sample ID.

    Returns:
        attempt_number (1-based index) on success, or -1 on failure.
    """
    outfile = os.path.join(outdir, f"{sample_id}.json")

    for attempt_number in range(retry_times):
        delay = pause * attempt_number
        if delay > 0:
            debug(
                f"[DEBUG] Sleeping {delay:.2f} seconds before attempt "
                f"{attempt_number + 1} for {sample_id}",
                verbose,
            )
        time.sleep(delay)

        debug(
            f"[INFO] Running ffq attempt {attempt_number + 1}/{retry_times} "
            f"for {sample_id}: {ffq_bin} -o {outfile} {sample_id}",
            verbose,
        )

        success, retry = ffq(sample_id, outfile, ffq_bin=ffq_bin, verbose=verbose)

        if success:
            # Check JSON content
            if load_json(outfile, sample_id, verbose=verbose):
                debug(
                    f"[INFO] ffq succeeded for {sample_id} "
                    f"on attempt {attempt_number + 1}",
                    verbose,
                )
                return attempt_number + 1
            else:
                # JSON invalid -> consider this a failed attempt, no retry flag here
                debug(
                    f"[ERROR] JSON validation failed for {sample_id} "
                    f"on attempt {attempt_number + 1}",
                    verbose,
                )
                # we can still retry if attempts remain
                continue

        if not success and not retry:
            debug(
                f"[ERROR] Unrecoverable ffq error for {sample_id} "
                f"on attempt {attempt_number + 1}, aborting.",
                verbose,
            )
            break

        if not success and retry:
            debug(
                f"[INFO] ffq indicated retry for {sample_id} "
                f"(attempt {attempt_number + 1}).",
                verbose,
            )
            # loop continues for another attempt

    debug(f"[ERROR] Exhausted retries for {sample_id}.", verbose)
    return -1


def ensure_outdir(path, verbose=False):
    """Ensure the output directory exists."""
    if not os.path.exists(path):
        debug(f"[DEBUG] Creating output directory: {path}", verbose)
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            print(f"[ERROR] Could not create output directory {path}: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wrapper around ffq with retry and error handling."
    )
    parser.add_argument(
        "IDs",
        help="Accession ID(s)",
        nargs="+",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Output directory [default: %(default)s]",
        default=".",
    )
    parser.add_argument(
        "-r",
        "--retry",
        type=int,
        help="Retry up to INT times [default: %(default)s]",
        default=4,
    )
    parser.add_argument(
        "-p",
        "--pause-after",
        type=float,
        help="Pause for (attempt * FLOAT) seconds [default: %(default)s]",
        default=10.0,
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        help="Number of threads (currently unused) [default: %(default)s]",
        default=1,
    )
    parser.add_argument(
        "-b",
        "--ffq-bin",
        help="Path to ffq executable [default: %(default)s]",
        default="ffq",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose/debug output",
        action="store_true",
    )

    args = parser.parse_args()

    ensure_outdir(args.output_dir, verbose=args.verbose)

    if not check_ffq(args.ffq_bin, verbose=args.verbose):
        print(f"ERROR: ffq is not installed or not executable: {args.ffq_bin}", file=sys.stderr)
        sys.exit(1)

    samples_status = {}

    for ID in args.IDs:
        debug("\n---------------------", args.verbose)
        debug(f"[INFO] Processing {ID}", args.verbose)

        attempt = tryFFQ(
            ID,
            args.output_dir,
            retry_times=args.retry,
            pause=args.pause_after,
            verbose=args.verbose,
            ffq_bin=args.ffq_bin,
        )

        if attempt > 0:
            debug(f"[INFO] Success {ID} (attempt={attempt})", args.verbose)
            samples_status[ID] = f"pass, ffq ({attempt})"
        else:
            debug(f"[INFO] Failed {ID}", args.verbose)
            samples_status[ID] = "failed"

    for sample, status in samples_status.items():
        print(f"{sample}: {status}")

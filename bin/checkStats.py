#!/usr/bin/env python
"""
Check consistency between a SeqFu stats file and an optional list of expected
sample IDs, and optionally attempt to re-download missing SRA entries.

This script:

1. Reads a tab-delimited SeqFu stats file (typically produced by `seqfu stats`),
   where each line corresponds to a sequence file with associated statistics.
2. Optionally reads a list of expected sample IDs (one per line, comments
   starting with '#' allowed).
3. For each ID in the list:
   - Counts how many stats-file entries contain that ID in their filename.
   - Checks whether all matched files have the same read count (#Seq).
   - Reports:
       * `<ID>\t<N>files` when counts are consistent.
       * `<ID>\t<N>files\tUNEVEN` when read counts differ across files.
   - If no file is found for an ID:
       * Optionally attempts to "rescue" it by running `fasterq-dump`
         (SRA Toolkit) into the specified output directory.
         Successful rescues are reported as `<ID>\t1+ files\tRESCUED`.
         Failures are reported as `<ID>\t0 files\t(NOT FOUND)`.

Exit codes:
    0  - Success (even if some IDs are missing, unless --fail is set).
    1  - Missing IDs and --fail was provided.

Typical usage:
    python check-stats.py --stats seqfu_stats.tsv --list sra_ids.txt \\
        --threads 4 --outdir fastq/ --fail --verbose
"""

import argparse
import subprocess
import sys


def check_sra(bin="fasterq-dump"):
    """
    Check if the SRA Toolkit `fasterq-dump` binary is available.

    Parameters
    ----------
    bin : str
        Name or path of the `fasterq-dump` binary to check.

    Returns
    -------
    bool
        True if the command can be executed with the `-h` flag, False otherwise.
    """
    try:
        subprocess.check_output([bin, "-h"])
        return True
    except Exception:
        return False


def loadstats(file):
    """
    Load a SeqFu stats file into a dictionary.

    The stats file is expected to be tab-delimited, with a header line starting
    with "File\\t#Seq\\t". Each subsequent line is assumed to have at least
    two columns: the file path/name and the number of sequences (#Seq),
    followed by any additional columns.

    Parameters
    ----------
    file : str
        Path to the stats file.

    Returns
    -------
    dict
        A dictionary mapping:
            file_name (str) -> list of remaining columns (list of str)
        where index 0 of the value list is typically the read count (#Seq).

    Notes
    -----
    On error, this function writes an error message to stderr and terminates
    the program.
    """
    stats = {}
    try:
        with open(file, "r") as f:
            for line in f:
                # Skip header line (or any line starting with this prefix)
                if line.startswith("File\t#Seq\t"):
                    continue
                fields = line.strip().split("\t")
                if not fields or len(fields) < 2:
                    # Skip malformed or empty lines silently
                    continue
                # Use the first field (file name/path) as the key
                stats[fields[0]] = fields[1:]

        return stats
    except Exception as e:
        # We check here and exit, no need to return errors to main
        print(
            "ERROR: Unable to read stats '%s':\n %s" % (file, e),
            file=sys.stderr,
        )
        sys.exit(1)


def loadfile(file):
    """
    Load a plain-text file containing one ID per line.

    Lines starting with '#' or blank lines are ignored.

    Parameters
    ----------
    file : str
        Path to the ID list file.

    Returns
    -------
    list of str
        List of IDs (one per non-comment, non-empty line).

    Notes
    -----
    On error, this function writes an error message to stderr and terminates
    the program.
    """
    lines = []
    try:
        with open(file, "r") as f:
            for line in f:
                line = line.strip()
                # Skip comment or empty lines
                if line.startswith("#") or len(line) < 1:
                    continue

                lines.append(line)

        return lines
    except Exception as e:
        # We check here and exit, no need to return errors to main
        print(
            "ERROR: Unable to read IDs list '%s':\n %s" % (file, e),
            file=sys.stderr,
        )
        sys.exit(1)


def tryFasterDump(id, outdir, threads=1, verbose=False):
    """
    Attempt to download an SRA run using `fasterq-dump`.

    Parameters
    ----------
    id : str
        SRA run accession (e.g. SRR1234567).
    outdir : str
        Output directory where FASTQ files will be written.
    threads : int, optional
        Number of threads to pass to `fasterq-dump`.
    verbose : bool, optional
        If True, print additional information and logs to stderr.

    Returns
    -------
    bool
        True if `fasterq-dump` finishes successfully, False otherwise.
    """
    cmd = ["fasterq-dump", "--threads", str(threads), "-O", outdir, id]

    if verbose:
        print(
            "[INFO] Running fasterq-dump: %s" % (" ".join(cmd)),
            file=sys.stderr,
        )

    # Capture stderr so we can show logs if needed
    fasterProc = subprocess.Popen(cmd, stderr=subprocess.PIPE)

    try:
        # Timeout after 2 hours (2 * 60 * 60 seconds)
        outs, errs = fasterProc.communicate(timeout=2 * 60 * 60)
        if verbose:
            print("   info: %s" % (outs), file=sys.stderr)
            print("   log: %s" % (errs), file=sys.stderr)

        # Check exit status
        if fasterProc.returncode != 0:
            print(
                "  [ERROR] Error running fasterq-dump: %s" % (errs),
                file=sys.stderr,
            )
            return False
        return True
    except subprocess.TimeoutExpired as e:
        # Kill process if it exceeds the timeout
        fasterProc.kill()
        outs, errs = fasterProc.communicate()
        print("[STDOUT] %s" % outs, file=sys.stderr)
        print("[STDERR] %s" % errs, file=sys.stderr)
        print("[ERROR] Timeout for fasterq-dump: %s" % (e), file=sys.stderr)
        return False


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(
        prog="check-stats",
        description=(
            "Check SeqFu stats against a list of SRA IDs and optionally "
            "attempt to rescue missing runs using fasterq-dump."
        ),
    )
    parser.add_argument(
        "--stats",
        help="SeqFu stats file (tab-delimited output from 'seqfu stats')",
        required=True,
    )
    parser.add_argument(
        "--list",
        help="File with one SRA ID per line (optional comments starting with '#')",
    )
    parser.add_argument(
        "--threads",
        help="Number of threads for fasterq-dump [default: %(default)s]",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--outdir",
        help="Output directory for rescued SRA runs [default: %(default)s]",
        default=".",
    )

    parser.add_argument(
        "--fail",
        help="Exit with status 1 if missing files are detected",
        action="store_true",
    )
    parser.add_argument(
        "--rescue",
        help="Attempt to rescue missing files using fasterq-dump",
        action="store_true",
    )
    parser.add_argument(
        "--verbose",
        help="Verbose mode",
        action="store_true",
    )

    args = parser.parse_args()

    # Load statistics table
    stats = loadstats(args.stats)

    # Check availability of SRA Toolkit (fasterq-dump)
    has_sra = check_sra()
    if args.verbose:
        print(
            "[INFO] SRA toolkit (fasterq-dump) found: %s" % (has_sra),
            file=sys.stderr,
        )

    if args.list:
        # List of expected IDs
        ids = loadfile(args.list)

        # Map: ID -> list of stat-file keys containing that ID
        files_per_id = {}

        # Lists to collect problematic IDs
        missing_ids = []
        bad_counts_ids = []
        rescued_ids = []

        # First pass: associate each stats-entry (file) with matching IDs
        for id in ids:
            for readfile in stats:
                # NOTE: substring matching: ID only needs to appear in the filename
                if id in readfile:
                    if id in files_per_id:
                        files_per_id[id].append(readfile)
                    else:
                        files_per_id[id] = [readfile]

        # Second pass: inspect each ID
        for id in ids:
            if id in files_per_id:
                # Check that all files for a given ID have consistent read counts
                counts = -1
                for file in files_per_id[id]:
                    current_count = stats[file][0]
                    if counts == -1:
                        counts = current_count
                    elif counts != current_count:
                        print(
                            "File %s has %s reads, expected %s"
                            % (file, current_count, counts),
                            file=sys.stderr,
                        )
                        bad_counts_ids.append(id)

                if id not in bad_counts_ids:
                    # All counts are consistent
                    print(id, "\t", len(files_per_id[id]), "files", sep="")
                else:
                    # At least one file has an inconsistent read count
                    print(
                        id,
                        "\t",
                        len(files_per_id[id]),
                        "files\tUNEVEN",
                        sep="",
                    )

            else:
                # No matching files found in the stats for this ID
                success = False
                # Only attempt rescue if both SRA tools are available and --rescue is set
                if has_sra and args.rescue:
                    success = tryFasterDump(
                        id,
                        args.outdir,
                        threads=args.threads,
                        verbose=args.verbose,
                    )

                if success:
                    print(id, "\t", "1+ files\tRESCUED", sep="")
                    rescued_ids.append(id)
                else:
                    print(id, "\t0 files\t(NOT FOUND)", sep="")
                    missing_ids.append(id)

        if len(rescued_ids) > 0:
            print(
                "[INFO] Rescued %i IDs" % (len(rescued_ids)),
                file=sys.stderr,
            )

        # Final summary and exit code logic
        if len(missing_ids) > 0 or len(bad_counts_ids) > 0:
            if len(bad_counts_ids) > 0:
                print(
                    "WARNING: uneven counts from files for IDs: ",
                    ",".join(bad_counts_ids),
                    file=sys.stderr,
                )
            if len(missing_ids) > 0:
                print(
                    "ERROR: missing IDs in stats: ",
                    ",".join(missing_ids),
                    file=sys.stderr,
                )
                if args.fail:
                    sys.exit(1)

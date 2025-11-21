#!/usr/bin/env python3
"""
Check internet connectivity by running several commands in parallel.
Use -v / --verbose to print full command output.
"""

import subprocess
import time
import sys
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

CHECK_COMMANDS = [
    ["ping", "-c", "3", "google.com"],
    ["curl", "-I", "https://ifconfig.me"],
    ["curl", "-I", "https://linuxconfig.org"],
    ["wget", "-qO-", "github.com"],
    ["wget", "-qO-", "bing.com"],
]


def parse_args():
    parser = argparse.ArgumentParser(description="Check Internet connectivity")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output and show command results",
    )
    return parser.parse_args()


def setup_logging(verbose: bool) -> logging.Logger:
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return logging.getLogger(__name__)


def run_single_check(cmd, verbose: bool) -> bool:
    """
    Run a single connectivity check command.
    Returns True if it succeeds, False otherwise.
    """
    logger = logging.getLogger(__name__)
    logger.debug("Starting command: %s", cmd)

    try:
        if verbose:
            # Show output directly
            subprocess.check_call(cmd)
        else:
            # Quiet mode
            subprocess.check_call(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        logger.debug("Command succeeded: %s", cmd)
        return True
    except subprocess.CalledProcessError as e:
        logger.warning("Command failed: %s (exit %s)", cmd, e.returncode)
    except FileNotFoundError:
        logger.warning("Command not found: %s", cmd[0])
    except Exception as e:
        logger.warning("Unexpected error running %s: %s", cmd, e)

    return False


def run_check_parallel(verbose: bool = False) -> bool:
    logger = logging.getLogger(__name__)
    start = time.time()

    logger.info(
        "Checking Internet connection using %d methods (in parallel)",
        len(CHECK_COMMANDS),
    )

    # Map each future to its command for logging
    with ThreadPoolExecutor(max_workers=len(CHECK_COMMANDS)) as executor:
        future_to_cmd = {
            executor.submit(run_single_check, cmd, verbose): cmd
            for cmd in CHECK_COMMANDS
        }

        # As soon as we get a success, we can stop checking results
        for idx, future in enumerate(as_completed(future_to_cmd), start=1):
            cmd = future_to_cmd[future]
            logger.info("Result received for command #%d: %s", idx, cmd)
            try:
                ok = future.result()
            except Exception as e:
                logger.warning("Command raised an unexpected exception: %s (%s)", cmd, e)
                ok = False

            if ok:
                duration = time.time() - start
                logger.info(
                    "Internet connection is UP (first success: %s, %.2f seconds)",
                    cmd,
                    duration,
                )
                return True

    duration = time.time() - start
    logger.error(
        "Internet connection is DOWN after %d commands (%.2f seconds)",
        len(CHECK_COMMANDS),
        duration,
    )
    return False


if __name__ == "__main__":
    args = parse_args()
    logger = setup_logging(args.verbose)
    ok = run_check_parallel(verbose=args.verbose)
    sys.exit(0 if ok else 1)

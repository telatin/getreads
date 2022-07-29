#!/usr/bin/env python
"""
Try to "ping -c 3 google.com" and "curl ifconfig.me", and if both fail,
then assume that the internet is down
"""


import subprocess
import time
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]    %(message)s')
logger = logging.getLogger(__name__)
start_time = time.time()
cmds = [
    ["ping", "-c", "3", "google.com"],
    ["wget", "--output-document", "-", "github.com"],
    ["wget", "--output-document", "-", "bing.com"],
    ["curl", "-I", "https://linuxconfig.org"],
    ["curl", "ifconfig.me"]
]
logger.info("Checking for Internet connection with %s commands", len(cmds))

attempts = 0
for cmd in cmds:
    attempts += 1
    logger.info(" -> Trying %s", cmd)
    try:
        test = subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("Internet connection is up: %s attempt(s)", attempts)
        sys.exit(0)
    except Exception as e:
        logger.warning("%s failed: %s", cmd, e)
        pass

logger.error("No internet connection detected using %s commands in %s seconds" % (
    attempts, time.time() - start_time))
exit(1)
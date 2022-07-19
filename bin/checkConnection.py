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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
start_time = time.time()
cmds = [
    ["curl", "-I", "https://linuxconfig.org"],
    ["ping", "-c", "3", "google.com"],
    ["curl", "ifconfig.me"],
    [""]
]
logger.info("Checking for Internet connection with %s commands", len(cmds))
for cmd in cmds:
    try:
        test = subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        logger.info("%s succeeded: Internet available in %s seconds", cmd, "{:.2f}".format(time.time() - start_time))
        sys.exit(0)
    except subprocess.CalledProcessError:
        logger.error("%s failed", cmd)
        pass

print("No internet connection detected using %s commands in %s seconds" % (
    len(cmds), time.time() - start_time))
exit(1)
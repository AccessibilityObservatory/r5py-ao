#!/usr/bin/env python3

"""Make sure R5 is in the class path, download it if not."""

import hashlib
import os.path
import sys

import xdg.BaseDirectory

from . import config
from .validatingrequestssession import ValidatingRequestsSession

# update these to use a newer R5 version
R5_JAR_URL = "https://github.com/conveyal/r5/releases/download/v6.6/r5-v6.6-all.jar"
R5_JAR_SHA256 = "9e4ceb85a09e750f146f95d98013eb164afac2dfc900a9e68e37ae925b1ec702"
# ---


__all__ = ["R5_CLASSPATH"]


CACHE_DIR = xdg.BaseDirectory.save_cache_path(__package__.split(".")[0])


config.argparser.add(
    "-r",
    "--r5-classpath",
    help="R5’s class path, can point to r5-all.jar",
    default="/usr/share/java/r5/r5-all.jar",
)
arguments = config.arguments()


if os.path.exists(arguments.r5_classpath):
    # do not test local files’ checksums, as they might be customly compiled
    R5_CLASSPATH = arguments.r5_classpath
else:
    R5_CLASSPATH = os.path.join(CACHE_DIR, os.path.basename(R5_JAR_URL))
    try:
        with open(R5_CLASSPATH, "rb") as jar:
            assert hashlib.sha256(jar.read()).hexdigest == R5_JAR_SHA256
    except (AssertionError, FileNotFoundError):
        if arguments.verbose:
            print(
                "Could not find R5 jar, trying to download it from upstream",
                file=sys.stderr,
                flush=True,
            )
        with ValidatingRequestsSession as session, session.get(
            R5_JAR_URL, R5_JAR_SHA256
        ) as response, open(R5_CLASSPATH, "wb") as jar:
            jar.write(response.content)

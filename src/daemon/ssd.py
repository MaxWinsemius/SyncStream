#!/usr/bin/env python

"""
The syncstraem daemon, that keeps track of the animations that run, and prepares the system to make sure that the
udpserver can run.

@author MaxWinsemius
@date 28-05-2022

TODO:
- Move many of these classes to their own files.
- Test generic working of this code.
- Add more configuration and argument options instead.
- Remove repeating code (this and udpserver/interface/sovereign.py share a lot of code)

DESIGN:
Animation class should handle adding and removing animations, changing config files and overwriting specific options
from the config files (for easy dynamic use of a generic template).
"""

import os
import sys
import sockets
import argparse
from enum import Enum

from Log import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Synsctream Daemon - Administrative daemon for the synsctream animations."
    )

    paths = {
        "socket": "/run/syncstream/ssd.socket",
        "animations": "src/animations/"
    }

    n = os.fork()
    if n == 0:
        s = sockets.Socket(paths["socket"], paths["animations"])
        s.serve_forever()

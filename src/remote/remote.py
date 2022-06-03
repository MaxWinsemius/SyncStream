"""
@author Max Winsemius
@date 28-05-2022
"""

import os
import sys
import argparse
import subprocess

from . import commands

def init_run():
    print("Creating {run} folder", file = sys.stderr)
    if not os.path.isfile(run):
        subprocess.call(f"sudo mkdir {run}".split(" "))
        subprocess.call(f"sudo chown {os.getlogin()}:{os.getlogin()} {run}".split(" "))

    if not os.access(run, os.R_OK) or not os.access(run, os.W_OK) or not os.access(run, os.X_OK):
        subprocess.call(f"sudo chown {os.getlogin()}:{os.getlogin()} {run}".split(" "))

parser = argparse.ArgumentParser(
    description = "SyncStream Remote - the cli tool for your SyncStream Daemon!",
)

parser.add_argument('-r', '--run', default = "/run/syncstream", help = 'The run folder in which syncstream creates sockets')

subparsers = parser.add_subparsers()

for command in commands.all:
    command.add_parser_subcommand(subparsers)

args = parser.parse_args()

from pprint import pprint
pprint(args)

run = args.run

for command_obj in commands.all:
    command = command_obj.__name__.split('.')[-1]
    if hasattr(args, command):
        # TODO: Add command_obj.requires:
        # - "run": needs the /run folder (or whatever is being used)
        # - "ssd": needs the ssd to be running
        # - more?

        if "run" in command_obj.requires:
            init_run()

        command_obj.exec(args)

"""
@author Max Winsemius
@date 28-05-2022
"""

import argparse

from . import commands

parser = argparse.ArgumentParser(
    description = "SyncStream Remote - the cli tool for your SyncStream Daemon!",
)

subparsers = parser.add_subparsers()

for command in commands.all:
    command.add_parser_subcommand(subparsers)

args = parser.parse_args()

from pprint import pprint
pprint(args)

for command_obj in commands.all:
    command = command_obj.__name__.split('.')[-1]
    if hasattr(args, command):
        command_obj.exec(args)

print("exiting")

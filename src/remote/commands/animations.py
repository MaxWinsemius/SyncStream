"""
@author Max Winsemius
@date 25-05-2022
"""

requires = ["ssd"]

def add_parser_subcommand(parser):
    p = parser.add_parser('animations', help = "Manage the animations running on this machine")

    sub = p.add_subparsers(dest = "animations")

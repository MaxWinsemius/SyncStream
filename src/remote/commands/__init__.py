"""
@author Max Winsemius
@date 24-05-2022
"""

from . import udpserver
from . import animations
from . import ssd

# Required methods for commands are:
# def add_parser_subcommand(parser):
#     pass
#
# def exec(args):
#     pass

all = [
    udpserver,
    animations,
    ssd
]

"""
@author Max Winsemius
@date 24-06-2022
"""

requires = ["ssd"]

def add_parser_subcommand(parser):
    p = parser.add_parser('ssd', help = "Manage the SyncStream Daemon")
    #p.add_argument('-a', '--animation-folder', default = "src/animations/", help = "Location of the folder containing animation programs") # TODO: implement this
    #p.add_argument('-s', '--socket', default = "ssd.socket", help = "The name of the socket") # TODO: implement this


def exec(args):
    # Start animation
        # nondefault config file param
    # Stop animation
    # List animations
    # List animation programs
    pass

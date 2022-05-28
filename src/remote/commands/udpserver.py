"""
@author Max Winsemius
@date 24-05-2022
"""

import sys

# This command will at least require the run folder to exist and be writable
requires = ["run"]

def add_parser_subcommand(parser):
    p = parser.add_parser('udpserver', help = "Manage the udp server on this machine")

    sub = p.add_subparsers(dest = "udpserver")

    # Commands
    start = sub.add_parser('start', help = "Start the UDP server")
    start.add_argument('-c', '--config', type = ascii, default = "src/udpserver/default.yaml", help = "The configuration file to load")

    sub.add_parser('stop', help = "Stop the UDP server")
    sub.add_parser('sockets', help = "List all the available sockets")
    sub.add_parser('dump-interfaces', help = "Dump the interface config")
    sub.add_parser('interfaces', help = "List the root interfaces")

    layers = sub.add_parser('layers', help = "Manage the layers of the UDP server")
    layers_sub = layers.add_subparsers(dest = "layers")
    layers.add_argument('interface', help = "This root interface should be used")

    layers_add = layers_sub.add_parser('add', help = "Add a new layer")
    layers_add.add_argument('index', type = int, help = "The index of where to insert the layer")
    layers_add.add_argument('-a', '--authorative', action = 'store_true', help = "Make this layer authoritive over the underlying layers. That means it is not transparent to underlying layers, but layers above can write over this layer.")

    layers_del = layers_sub.add_parser('delete', help = "Delete a layer")
    layers_del.add_argument('index', type = int, help = "The index of the layer to remove")

def exec(args):
    command = args.udpserver

    if command == "start":
        print("starting server")
        config = args.config
        start(config)

    elif command == "stop":
        print("stopping server")

    elif command == "sockets":
        print("listing udpsockets")

    elif command == "dump-interfaces":
        print("dumping interface config")

    elif command == "sockets":
        print("listing root interfaces")

    elif command == "layers":
        print("manage the layers of this server")

    else:
        print("Unknown command used!", file = sys.stderr)

def start(config):
    pass

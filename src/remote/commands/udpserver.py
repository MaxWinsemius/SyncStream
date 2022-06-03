"""
@author Max Winsemius
@date 24-05-2022
"""

import os
import sys

# This command will at least require the run folder to exist and be writable
requires = ["run"]
run = None

def add_parser_subcommand(parser):
    p = parser.add_parser('udpserver', help = "Manage the udp server on this machine")
    p.add_argument('-s', '--server', default = "src/udpserver/udpserver.py", help = "Location of the udpserver.py file")

    sub = p.add_subparsers(dest = "udpserver")

    # Commands
    start = sub.add_parser('start', help = "Start the UDP server")
    start.add_argument('-c', '--config', default = "src/udpserver/default.yaml", help = "The configuration file to load")

    sub.add_parser('stop', help = "Stop the UDP server")
    sub.add_parser('dump-interfaces', help = "Dump the interface config")
    sub.add_parser('interfaces', help = "List the root interfaces")

    layers = sub.add_parser('layers', help = "Manage the layers of the UDP server")
    layers_sub = layers.add_subparsers(dest = "layers")
    layers.add_argument('interface', help = "This root interface should be used")

    layers_add = layers_sub.add_parser('add', help = "Add a new layer")
    layers_add.add_argument('index', type = int, help = "The index of where to insert the layer")
    layers_add.add_argument('-a', '--authorative', action = 'store_true', help = "Whenever this layer updates, the framebuffer will be send out. Every root interface needs at least a single authorative layer.")
    layers_add.add_argument('-o', '--overwrite', action = "store_true", help = "Overwrite any leds that are not set to 0")

    layers_del = layers_sub.add_parser('delete', help = "Delete a layer")
    layers_del.add_argument('index', type = int, help = "The index of the layer to remove")

def exec(args):
    command = args.udpserver

    if command == "start":
        cmd_start(args.config)

    elif command == "stop":
        cmd_stop()

    elif command == "dump-interfaces":
        cmd_dump_interfaces()

    elif command == "interfaces":
        cmd_list_interfaces()

    elif command == "layers":
        # parse the rest of this information
        pass

    else:
        print("Unknown command used!", file = sys.stderr)

def cmd_start(config):
    # Check if socket exists
    #if os.path.isfile("")
        # Check if server is already running with a ping / getinfo command
            # Error out noting that the server is already running

        # Remove the socket
    # Start the server
    pass

def cmd_stop():
    pass

def cmd_dump_interfaces():
    pass

def cmd_list_interfaces():
    global run
    for item in os.listdir(run):
        print(item)

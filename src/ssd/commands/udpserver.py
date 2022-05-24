"""
@author Max Winsemius
@date 24-05-2022
"""

def add_parser_subcommand(parser):
    p = parser.add_parser('udpserver', help = "Manage the udp server on this machine")

    sub = p.add_subparsers(dest = "udpserver")
    commands = sub.add_parser('start', help = "Start the UDP server")
    commands = sub.add_parser('stop', help = "Stop the UDP server")
    commands = sub.add_parser('sockets', help = "List all the available sockets")
    commands = sub.add_parser('dump-interfaces', help = "Dump the interface config")
    commands = sub.add_parser('interfaces', help = "List the root interfaces")

    layers = sub.add_parser('layers', help = "Manage the layers of the UDP server")
    layers_sub = layers.add_subparsers(dest = "layers")
    layers.add_argument('interface', help = "This root interface should be used")

    layers_add = layers_sub.add_parser('add', help = "Add a new layer")
    layers_add.add_argument('index', type = int, help = "The index of where to insert the layer")
    layers_add.add_argument('-a', '--authorative', action = 'store_true', help = "Make this layer authoritive over the underlying layers. That means it is not transparent to underlying layers, but layers above can write over this layer.")

    layers_del = layers_sub.add_parser('delete', help = "Delete a layer")
    layers_del.add_argument('index', type = int, help = "The index of the layer to remove")

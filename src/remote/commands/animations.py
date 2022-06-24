"""
@author Max Winsemius
@date 25-05-2022
"""

import sys

requires = ["ssd"]
run = None

def add_parser_subcommand(parser):
    p = parser.add_parser('animations', help = "Manage the animations with the help of the SyncStream Daemon")

    sub = p.add_subparsers(dest = "animations")

    # Commands
    start = sub.add_parser('start', help = "Start an animation")
    start.add_argument('animation', help = "The animation to start")
    start.add_argument('config', help = "The corresponding configuration file for the animation") # TODO: make this optional and parse default config?

    stop = sub.add_parser('stop', help = "Stop an animation")
    stop.add_argument('id', help = "The id of the animation to stop")

    sub.add_parser('running', help = "List all the currently running animations")
    sub.add_parser('all', help = "List all available animations")

def exec(args):
    command = args.animations

    if command == "start":
        print(f"Starting animation {args.animation} with conf {args.config}")

    elif command == "stop":
        print(f"Stopping animation {args.id}")

    elif command == "running":
        print("List all running animations")

    elif command == "all":
        print("Listing all available animations")

    else:
        print("Unknown command used!", file = sys.stderr)

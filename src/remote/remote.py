"""
@author Max Winsemius
@date 28-05-2022
"""

import os
import sys
import socket
import argparse
import subprocess

from . import commands

def init_run():
    if not os.path.isdir(run):
        print(f"Creating {run} folder", file = sys.stderr)
        subprocess.call(f"sudo mkdir {run}".split(" "))
        subprocess.call(f"sudo chown {os.getlogin()}:{os.getlogin()} {run}".split(" "))

    if not os.access(run, os.R_OK) or not os.access(run, os.W_OK) or not os.access(run, os.X_OK):
        print(f"Chowning {run} folder", file = sys.stderr)
        subprocess.call(f"sudo chown {os.getlogin()}:{os.getlogin()} {run}".split(" "))

def ping_ssd(path):
    try:
        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect(path)
            sock.sendall(bytes("TESLAN____________PING" + "\n", "utf-8"))
            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            print("Received: {}".format(received))
    except ConnectionRefusedError:
        return False

    return True

def init_ssd():
    ssd_socket_path = f"{run}/ssd.socket"
    if os.access(ssd_socket_path, os.R_OK) and os.access(ssd_socket_path, os.W_OK) and ping_ssd(ssd_socket_path):
        print("SSD ALREADY RUNNING ")
        return

    print("booting ssd ")
    subprocess.Popen("src/daemon/ssd.py")

parser = argparse.ArgumentParser(
    description = "SyncStream Remote - the cli tool for your SyncStream Daemon!",
)

parser.add_argument('-r', '--run', default = "/run/syncstream", help = 'The run folder in which syncstream creates sockets')

subparsers = parser.add_subparsers()

for command in commands.all:
    command.add_parser_subcommand(subparsers)

args = parser.parse_args()

#from pprint import pprint
#pprint(args)

run = args.run

for command_obj in commands.all:
    command = command_obj.__name__.split('.')[-1]
    if hasattr(args, command):
        # TODO: Add command_obj.requires:
        # - "run": needs the /run folder (or whatever is being used)
        # - "ssd": needs the ssd to be running
        # - more?

        if "run" in command_obj.requires or "ssd" in command_obj.requires:
            init_run()

        if "ssd" in command_obj.requires:
            init_ssd()

        command_obj.run = run
        command_obj.exec(args)

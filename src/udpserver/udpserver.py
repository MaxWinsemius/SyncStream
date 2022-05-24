#!/usr/bin/env python

"""
Usage: ./udpserver.py

@author Max Winsemius
@date 15-01-2022
"""

from interfaces import *
import yaml
import os, sys
from multiprocessing import Pool

sovereigns = []

def parse_interface(config):
    inf = None

    if config["interface-type"] == "virtual":
        inf = virtual.VirtualInterface()

        if len(config["children"]) < 1:
            raise ValueError(f"Virtual interface {config['name']} has no children")

        for child in config["children"]:
            inf.append_interface(parse_interface(child))

    elif config["interface-type"] == "physical":
        inf = physical.PhysicalInterface(config["ip"], config["port"], config["amount-leds"], config["max-udp-size"], config["max-brightness"])

    return inf

def launch_interface(root):
    print(f"Root interface {root['name']} found")
    sov = sovereign.Root(parse_interface(root), config["sockets"]["dir"] + "/" + root["name"])

if __name__ == '__main__':
    try: config_file = sys.argv[1]
    except IndexError:
        config_file = "example.yaml"

    with open(config_file) as fh:
        config = yaml.safe_load(fh)

    if len(config["interfaces"]) < 1:
        raise ValueError("No root interfaces found")

    if not os.path.exists(config["sockets"]["dir"]):
        os.mkdir(config["sockets"]["dir"])

    print("Starting root interface processes")
    with Pool(len(config["interfaces"])) as p:
        p.map(launch_interface, config["interfaces"])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 20:52:42 2022

@author: ostheer
"""

import yaml, sys, time
from .connection import Connection
# from .connection import DummyConnection as Connection
from .connection import CommandTypes



# channel
class Channel:
    def __init__(self, socket_path):
        self.path = socket_path
        self.socket = Connection(socket_path)
        self.info = yaml.safe_load(self.socket.get_something(CommandTypes.GET_INFO_CMD_ID))

        self.length = self.info["num_leds"]
        self.buffer = [[0,0,0] for _ in range(self.length)]

    def dispatch(self):
        if any(x>1 or x<0 for x in [e for E in self.buffer for e in E]): raise ValueError("Subcolour must be between 0 and 1!")
        self.socket.send_buffer([[round(r*255), round(g*255), round(b*255)] for r,g,b in self.buffer])

    def putled(self, i, brightness=1):
        try:
            if brightness:
                self.buffer[i]  = [c*brightness for c in self.colour]
            else:
                self.buffer[i]  = [0, 0, 0]
        except IndexError:
            pass

# general animation framework
class Animation:
    def __init__(self, config_file=None):
        #load configuration file
        if config_file is None:
            try: config_file = sys.argv[1]
            except IndexError:
                config_file = sys.argv[0].split(" ")[-1].strip()
                if config_file.endswith(".py"): config_file = "".join(config_file.split(".py")[:-1])
                config_file = config_file + ".yaml"
        with open(config_file, "r") as f:
            self.config = yaml.safe_load(f)

        assert self.config["target_animation"] == self.__class__.__name__, "Wrong config file for this animation!"

        #parse required animation parameters
        try:
            self.delay = lambda: time.sleep(1/self.config["parameters"]["update_rate"])
            self.speed = self.config["parameters"]["speed"]
        except KeyError:
            raise KeyError("Config file doesn't contain required information")

        #connect to sockets
        self.channels = [Channel(socket_path) for socket_path in self.config["sockets"]]

        #blank leds
        for ch in self.channels:
            for i in range(ch.length):
                ch.putled(i, 0)
            ch.dispatch()

    def __call__(self):
        print(f"Starting animation '{self.__class__.__name__}' on sockets {', '.join([ch.path for ch in self.channels])}.")
        try:
            self._animate()
        except KeyboardInterrupt:
            print("\rStopping animation...")

class TooManySinksException(Exception):
    pass

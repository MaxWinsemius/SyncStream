#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
./knight_rider.py knight_rider_config.yaml

Created on Sat Jan 15 20:42:47 2022

@author: ostheer
"""

from python_animation_lib.animation import Animation
from functools import wraps

class KnightRider(Animation):
    # Extend constructor to parse more animation parameters
    @wraps(Animation.__init__)
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        try:
            self.colour = self.config["parameters"]["colour"]
            self.tail_length = self.config["parameters"]["tail_length"]
        except KeyError:
            raise KeyError("Config file doesn't contain required information")

    # Main method that performs the animation
    def _animate(self):
        def putled(channel, i):
            channel.buffer[i]  = self.colour

        def decrement(channel):
            for i, led in enumerate(channel.buffer):
                channel.buffer[i] = [max(0, c-1/self.tail_length) for c in led]

        positions  = [0    for _ in self.channels]
        directions = [True for _ in self.channels]

        while True:
            for i, channel in enumerate(self.channels):
                for _ in range(round(self.speed)):
                    decrement(channel)
                    putled(channel, positions[i])

                    positions[i] += 2*directions[i] - 1
                    if positions[i] <= 0 or positions[i] >= channel.length-1:
                        directions[i] = not directions[i]
                channel.dispatch()

            self.delay()

if __name__ == "__main__":
    a = KnightRider()()

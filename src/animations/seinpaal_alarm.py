#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
./knight_rider.py knight_rider_config.yaml

Created on Sat Jan 15 20:42:47 2022

@author: ostheer
"""

from python_animation_lib.animation import Animation
from python_animation_lib.seinpaal import SeinpaalMixin
from python_animation_lib.helpers import set_channel_prop
from functools import wraps
from math import pi, ceil

class SeinpaalAlarm(SeinpaalMixin, Animation):
    # Extend constructor to parse more animation parameters
    @wraps(Animation.__init__)
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        try:
            for prop in ("led_spacing", "paal_radius", "colour"):
                set_channel_prop(self, prop, self.config["parameters"][prop])
            
            for ch in self.channels:
                ch.ringsize = 2*ch.paal_radius*pi/ch.led_spacing
            
        except KeyError:
            raise KeyError("Config file doesn't contain required information")

    # Main method that performs the animation
    def _animate(self):
        rad = 0
        while True:
            rad += .1
            rad = rad%(2*pi)

            for i, channel in enumerate(self.channels):
                for j in range(ceil(channel.length/channel.ringsize)):
                    channel.putled(*self.get_index(channel, j, rad))
                    channel.putled(*self.get_index(channel, j, rad+pi))
                channel.dispatch()
            
                for i in range(len(channel.buffer)):
                    channel.putled(i, 0)
            
            self.delay()

if __name__ == "__main__":
    a = SeinpaalAlarm()()

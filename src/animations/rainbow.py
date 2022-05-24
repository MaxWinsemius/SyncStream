#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
./rainbow.py rainbow.yaml

Created on Thu Feb 24 01:09:10 2022

@author: Hernivo
"""

from python_animation_lib.animation import Animation
from functools import wraps
import colorsys

#%% Helpers
hsv2rgb = lambda h,s,v: tuple(int(x * 15) for x in colorsys.hsv_to_rgb(h,s,v))

class Rainbow(Animation):
    # Extend constructor to parse more animation parameters
    @wraps(Animation.__init__)
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        try:
            self.update_rate = self.config["parameters"]["update_rate"]
        except KeyError:
            raise KeyError("Config file doesn't contain required information")

    # Main method that performs the animation
    def _animate(self):
        def cycle(arr, s=1):
            def _cycle0(arr): return [*arr[1:], arr[0]]
            def _cycle1(arr): return [arr[-1], *arr[:-1]]
            for _ in range(abs(s)):
                if s>0: arr = _cycle0(arr)
                else:   arr = _cycle1(arr)
            return arr

        Nsteps = self.update_rate

        buffers = [[(x*1.0/channel.length, 1, 1) for x in range(channel.length)] for channel in self.channels]

        while True:
            for i, channel in enumerate(self.channels):
                for j, val in enumerate(buffers[i]):
                    channel.buffer[j] = [x / 15 for x in hsv2rgb(*val)]
                buffers[i] = cycle(buffers[i], self.speed)
                channel.dispatch()

            self.delay()

if __name__ == "__main__":
    a = Rainbow()()

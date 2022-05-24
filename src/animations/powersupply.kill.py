#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
./powersupply.kill.py powersupply.kill.yaml

Created on Wen 23 Feb 21:18:18 2022

@author: Hernivo
"""

from python_animation_lib.animation import Animation
from functools import wraps
import random
import time

class Powersupply_kill(Animation):
    # Extend constructor to parse more animation parameters
    @wraps(Animation.__init__)
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        try:
            self.flame_colour = self.config["parameters"]["flame_colour"]
            self.flame_colour_fade = self.config["parameters"]["flame_colour_fade"]
            self.flame_dropdown_distance = self.config["parameters"]["flame_dropdown_distance"]
            self.flame_dropdown_chance = self.config["parameters"]["flame_dropdown_chance"]
            self.flicker_sleep = self.config["parameters"]["flicker_sleep"]
            self.flicker_times = self.config["parameters"]["flicker_times"]
            self.random_green_chance = self.config["parameters"]["random_green_chance"]
            self.random_green_flicker_pre_finish_sleep = self.config["parameters"]["random_green_flicker_pre_finish_sleep"]
            self.random_green_flicker_finish_sleep = self.config["parameters"]["random_green_flicker_finish_sleep"]
        except KeyError:
            raise KeyError("Config file doesn't contain required information")

    # Main method that performs the animation
    def _animate(self):
        def flame_write(channel, i):
            c = self.flame_colour
            channel.buffer[i]  = c

        def decrement(channel):
            for i, led in enumerate(channel.buffer):
                r, g, b = led
                channel.buffer[i] = [max(r - self.flame_colour_fade[0], 0),
                                     max(g - self.flame_colour_fade[1], 0),
                                     max(b - self.flame_colour_fade[2], 0)]

        def rand_add(base, mult):
            return base + random.randrange(int(base * - mult), int(base * mult))

        def flickerloop(channel, wake_time, sleep_time, repeats=3,
                        random_repeats=True, random_sleep=True, random_mult=0.8):

            if random_repeats:
                repeats = rand_add(repeats, 0.5)

            for _ in range(repeats):
                if random_sleep:
                    w = rand_add(wake_time, random_mult)
                    s = rand_add(sleep_time, random_mult)

                    if random.random() < 0.01:
                        w = 10 if random.random() < 0.5 else 10000
                        s = 10 if random.random() < 0.5 else 10000
                else:
                    w = wake_time
                    s = sleep_time

                flicker(channel, w / 1000, s / 1000)

        def flicker(channel, wake_time, sleep_time):
            channel.buffer = [[0,0,0] for _ in range(channel.length)]
            channel.dispatch()
            time.sleep(sleep_time)
            channel.buffer = [[1,1,1] for _ in range(channel.length)]
            channel.dispatch()
            time.sleep(wake_time)

        def green_glitter(channel, green_chance):
            channel.buffer = [[0, 0, 0] for _ in range(channel.length)]
            channel.dispatch()

            for l in range(channel.length):
                if random.random() < green_chance:
                    channel.buffer[l] = [0, random.random()**8, 0]

            channel.dispatch()

        positions  = [0    for _ in self.channels]
        directions = [True for _ in self.channels]

        # Animation cases:
        # 0 = building fire
        # 1 = backfilling to white
        # 2 = flickering white
        # 3 = random green leds on
        # 4 = random green leds flickering
        animation = 0

        for i, channel in enumerate(self.channels):
            channel.buffer = [[0.01, 0.0, 0.0] for _ in range(channel.length)]
            channel.dispatch()
            channel.buffer = [[0,0,0] for _ in range(channel.length)]
            channel.dispatch()
            time.sleep(0.01)

        while True:
            #print(animation)
            for i, channel in enumerate(self.channels):
                if animation == 0:
                    for _ in range(round(self.speed)):
                        decrement(channel)
                        flame_write(channel, positions[i])

                        if random.random() < self.flame_dropdown_chance:
                            positions[i] = max(0, round(positions[i] - (self.flame_dropdown_distance * channel.length)))
                        else:
                            positions[i] += 2*directions[i] - 1

                        if positions[i] >= channel.length:
                            animation = 1
                            positions[i] = channel.length - 1
                    channel.dispatch()

                elif animation == 1:
                    for _ in range(round(self.speed)):
                        channel.buffer[positions[i]] = [1, 1, 1]
                        positions[i] -= 1

                        if positions[i] <= 0:
                            animation = 2
                    channel.dispatch()

                elif animation == 2:
                    #time.sleep(self.flicker_sleep)
                    #for i in range(self.flicker_times):
                    #    flicker(channel, 0.5, 0.1)

                    flickerloop(channel, self.flicker_sleep, self.flicker_sleep * 0.2, repeats=self.flicker_times)

                    animation = 3

                elif animation == 3:
                    for _ in range(round(self.speed)):
                        green_glitter(channel, self.random_green_chance)
                        time.sleep(self.random_green_flicker_pre_finish_sleep)
                        animation = 4

                else:
                    green_glitter(channel, self.random_green_chance)
                    time.sleep(self.random_green_flicker_finish_sleep)

            self.delay()

if __name__ == "__main__":
    a = Powersupply_kill()()

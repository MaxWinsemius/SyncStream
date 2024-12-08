#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from python_animation_lib.animation import Animation
from functools import wraps
import random
import math

class Flame(Animation):
    @wraps(Animation.__init__)
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        try:
            self.speed = self.config["parameters"]["speed"]
            self.colour = self.config["parameters"]["colour"]
            self.update_rate = self.config["parameters"]["update_rate"]
        except KeyError:
            raise KeyError("Config file doesn't contain required information")

        # Flame configuration
        self.n_cols = 13
        self.top_flame_rows = 5       # The top rows with a stable flame
        self.wavy_rows_count = 10     # Number of rows below the stable flame that flicker sporadically

        self.base_flame_color = self.colour
        self.top_flame_flicker = 0.1          # Slight flicker at the top
        self.wavy_flicker_chance = 0.8         # Base probability each LED in wavy area flickers off
        self.wavy_flicker_intensity = 0.9      # Additional flicker intensity in wavy area

        self.ember_spawn_chance = 2          # Chance of spawning an ember
        self.ember_speed = 1                   # Rows per update embers move upward
        self.ember_decay = 0.9                 # Ember brightness decay per update
        self.ember_base_color = self.colour    # Ember color
        self.embers = [[] for _ in self.channels]  # Track embers per channel
        self.n_rows = 1

    def _animate(self):
        while True:
            for ch_index, channel in enumerate(self.channels):
                length = channel.length
                if length < self.n_cols:
                    for i in range(length):
                        channel.buffer[i] = (0,0,0)
                    channel.dispatch()
                    continue

                self.n_rows = max(length // self.n_cols,self.n_rows)
                n_rows = self.n_rows
                extra_leds = length % self.n_cols
                total_rows = n_rows + (1 if extra_leds > 0 else 0)

                # Flame structure:
                # Row 0 = top; row increases going downward
                stable_flame_end = min(self.top_flame_rows, total_rows)
                wavy_area_start = stable_flame_end
                wavy_area_end = min(wavy_area_start + self.wavy_rows_count, total_rows)
                # Embers spawn below wavy area
                ember_spawn_row = wavy_area_end if wavy_area_end < total_rows else total_rows - 1

                frame_buffer = [(0,0,0) for _ in range(length)]
                # 1. Draw top stable flame rows
                for row in range(stable_flame_end):
                    row_led_count = self.n_cols if row < n_rows else extra_leds
                    flicker = 1.0 + random.uniform(-self.top_flame_flicker, self.top_flame_flicker)
                    flicker = max(0, flicker)
                    for col in range(row_led_count):
                        idx = (total_rows - 1 - row) * self.n_cols + col
                        if idx < length:
                            r = min(1, self.base_flame_color[0] * flicker)
                            g = min(1, self.base_flame_color[1] * flicker)
                            b = min(1, self.base_flame_color[2] * flicker)
                            frame_buffer[idx] = (r, g, b)

                wavy_height = max(1, wavy_area_end - wavy_area_start - 1)
                for row in range(wavy_area_start, wavy_area_end):
                    row_led_count = self.n_cols if row < n_rows else extra_leds

                    # Compute progress along the wavy area
                    # If only one wavy row, progress stays at 0.
                    progress = 0.0
                    if wavy_height > 0:
                        progress = (row - wavy_area_start) / wavy_height

                    # Interpolate flicker chance and intensity
                    current_flicker_chance = self.wavy_flicker_chance * progress
                    current_flicker_intensity = self.wavy_flicker_intensity * progress

                    for col in range(row_led_count):
                        idx = (total_rows - 1 - row) * self.n_cols + col
                        if idx < length:
                            if random.random() < current_flicker_chance:
                                base_val = ((1-current_flicker_intensity) * random.random())*(1-wavy_height/(row-wavy_area_start))
                                r = min(1, self.base_flame_color[0] * base_val)
                                g = min(1, self.base_flame_color[1] * base_val)
                                b = min(1, self.base_flame_color[2] * base_val)
                            else:
                                flicker = 1.0 + random.uniform(-current_flicker_intensity, current_flicker_intensity)
                                flicker = max(0, flicker)
                                r = min(1, self.base_flame_color[0] * flicker)
                                g = min(1, self.base_flame_color[1] * flicker)
                                b = min(1, self.base_flame_color[2] * flicker)

                            frame_buffer[idx] = (r, g, b)

                # 3. Update and draw embers
                new_embers = []
                for ember in self.embers[ch_index]:
                    ember['row'] -= self.ember_speed / self.speed
                    ember['brightness'] *= self.ember_decay

                    if ember['row'] < 0 or ember['brightness'] < 0.05:
                        continue

                    erow = int(math.floor(ember['row']))
                    if erow < n_rows:
                        row_led_count = self.n_cols
                    elif erow == n_rows and extra_leds > 0:
                        row_led_count = extra_leds
                    else:
                        row_led_count = 0

                    if 0 <= erow < total_rows and row_led_count > 0:
                        if random.random() < 0.8:  # chance to flutter horizontally
                            if random.random() < 0.5:
                                ember['col'] = max(0, ember['col'] - 1)
                            else:
                                ember['col'] = min(self.n_cols - 1, ember['col'] + 1)

                        ecol = max(0, min(ember['col'], row_led_count - 1))
                        idx = erow * self.n_cols + ecol
                        if idx < length:
                            b = ember['brightness']
                            er = min(1, self.ember_base_color[0] * b)
                            eg = min(1, self.ember_base_color[1] * b)
                            eb = min(1, self.ember_base_color[2] * b)

                            base_r, base_g, base_b = frame_buffer[idx]
                            nr = min(1, base_r + er)
                            ng = min(1, base_g + eg)
                            nb = min(1, base_b + eb)
                            frame_buffer[idx] = (nr, ng, nb)

                            new_embers.append(ember)

                self.embers[ch_index] = new_embers

                # 4. Possibly spawn a new ember below the wavy area
                if ember_spawn_row < total_rows and ember_spawn_row >= 0:
                    if random.random() < self.ember_spawn_chance:
                        spawn_row = random.randint(ember_spawn_row, min(total_rows - 1, ember_spawn_row + 3))
                        new_ember = {
                            'col': random.randint(0, self.n_cols),
                            'row': float(spawn_row),
                            'brightness': random.uniform(0.5, 1.0)
                        }
                        self.embers[ch_index].append(new_ember)

                # Clamp and write to channel
                for i, color in enumerate(frame_buffer):
                    r, g, b = color
                    channel.buffer[i] = (max(0, min(r,1)), max(0, min(g,1)), max(0, min(b,1)))

                channel.dispatch()

            self.delay()

if __name__ == "__main__":
    a = Flame()()

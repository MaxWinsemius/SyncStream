#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from python_animation_lib.animation import Animation
from functools import wraps

class Barber(Animation):
    @wraps(Animation.__init__)
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        try:
            self.speed = self.config["parameters"]["speed"]
            self.colours = self.config["parameters"]["colours"]  # List of 3 RGB colours
            self.update_rate = self.config["parameters"]["update_rate"]
            self.num_strokes = self.config["parameters"]["num_strokes"]  # Number of diagonal strokes
            self.stroke_width = self.config["parameters"]["stroke_width"]
        except KeyError:
            raise KeyError("Config file doesn't contain required information")

        # Pole configuration
        self.n_cols = 13  # Assume 13 columns in the LED strip
        self.n_rows = 1
        self.shift_step = 1  # Number of steps to shift the pattern each frame
        self.pattern = []

    def generate_pattern(self):
        """
        Create the initial diagonal pattern for the barbershop pole.
        """
        self.pattern = []
        for row in range(self.n_rows):
            row_pattern = []
            for col in range(self.n_cols):
                # Determine the diagonal stroke based on row, column, and number of strokes
                # diagonal_index = (row + col) % self.num_strokes
                diagonal_index = ((row + col) // self.stroke_width) % self.num_strokes
                colour_index = diagonal_index % len(self.colours)  # Cycle through the 3 colours
                row_pattern.append(self.colours[colour_index])
            self.pattern.append(row_pattern)

    def rotate_pattern(self):
        """
        Rotate the pattern diagonally by shifting rows and columns.
        """
        self.pattern = [
            [self.pattern[(row - self.shift_step) % self.n_rows][(col - self.shift_step) % self.n_cols]
             for col in range(self.n_cols)]
            for row in range(self.n_rows)
        ]

    def _animate(self):
        while True:
            for ch_index, channel in enumerate(self.channels):
                length = channel.length
                if length < self.n_cols:
                    # Not enough LEDs for even one row
                    for i in range(length):
                        channel.buffer[i] = (0, 0, 0)
                    channel.dispatch()
                    continue

                self.n_rows = max(length // self.n_cols, self.n_rows)
                n_rows = self.n_rows
                extra_leds = length % self.n_cols
                total_rows = n_rows + (1 if extra_leds > 0 else 0)

                # Generate the initial pattern if not already done
                if not self.pattern or len(self.pattern) != self.n_rows:
                    self.generate_pattern()

                # Create a frame buffer
                frame_buffer = [(0, 0, 0) for _ in range(length)]

                # Apply the pattern to the LED strip
                for row in range(self.n_rows):
                    row_led_count = self.n_cols if row < n_rows else extra_leds
                    for col in range(row_led_count):
                        idx = (total_rows - 1 - row) * self.n_cols + col
                        if idx < length:
                            frame_buffer[idx] = self.pattern[row][col]

                # Rotate the pattern for the next frame
                self.rotate_pattern()

                # Write the frame buffer to the channel
                for i, colour in enumerate(frame_buffer):
                    r, g, b = colour
                    channel.buffer[i] = (max(0, min(r, 1)), max(0, min(g, 1)), max(0, min(b, 1)))

                channel.dispatch()
            self.delay()

if __name__ == "__main__":
    a = Barber()()

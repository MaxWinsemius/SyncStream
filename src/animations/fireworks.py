#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from python_animation_lib.animation import Animation
from functools import wraps
import random
import math

class Fireworks(Animation):
    @wraps(Animation.__init__)
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        try:
            self.speed = self.config["parameters"]["speed"]
            self.colour = self.config["parameters"]["colour"]  # RGB colour of the sparks
            self.update_rate = self.config["parameters"]["update_rate"]
            self.explosions_only = self.config["parameters"]["explosions_only"]  # Skip launch phase
            self.spawn_rate = self.config["parameters"]["spawn_rate"]  # Chance to spawn a spark
            self.explosion_size = self.config["parameters"]["explosion_size"]  # Size of the explosion
        except KeyError:
            raise KeyError("Config file doesn't contain required information")

        self.n_cols = 13  # Assume 13 columns in the LED strip
        self.n_rows = 1
        self.sparks = []

    def create_explosion(self, spark):
        """Spawn explosion sparks at the location of the main spark."""
        num_sparks = self.explosion_size * 5  # Number of explosion sparks
        max_distance = self.explosion_size  # Maximum travel distance
        explosion_sparks = []
        for _ in range(num_sparks):
            angle = random.uniform(0, 2 * math.pi)  # Random direction
            distance = random.uniform(1, max_distance)  # Random distance
            dx = math.cos(angle)
            dy = math.sin(angle)
            explosion_sparks.append({
                "col": spark["col"],
                "row": spark["row"]+1,
                "dx": dx,  # X velocity
                "dy": dy,  # Y velocity
                "distance_left": distance,  # Remaining travel distance
            })
        return explosion_sparks

    def launch_spark(self):
        """Spawn a new spark at a random position at the top row."""
        if random.random() < self.spawn_rate:
            spark = {
                "col": random.randint(0, self.n_cols - 1),  # Random column
                "row": self.n_rows - 1,  # Start at the top row
                "phase": "falling",  # Current phase: "falling" or "exploding"
                "brightness": 1.0,  # Initial brightness
                "target_row": random.randint(min(3,self.n_rows - 1), self.n_rows - 1),  # Random row for explosion
                "explosion_timer": self.explosion_size,  # Countdown for explosion decay
            }
            self.sparks.append(spark)

    def update_sparks(self):
        """Update the position and state of all sparks."""
        new_sparks = []
        for spark in self.sparks:
            if spark["phase"] == "falling":
                if self.explosions_only:
                    # Skip the falling phase if explosions_only is True
                    spark["phase"] = "exploding"
                    spark["row"] = random.uniform(1,self.n_rows-1)
                    spark["explosion_sparks"] = self.create_explosion(spark)
                else:
                    # Move spark downward
                    spark["row"] -= 1
                    if spark["row"] % 2 == 0:
                        spark["col"] -= 1
                    if spark["row"] <= spark["target_row"]:
                        # Spark reaches the explosion height
                        spark["phase"] = "exploding"
                        spark["explosion_sparks"] = self.create_explosion(spark)
                new_sparks.append(spark)
            elif spark["phase"] == "exploding":
                # Update explosion sparks
                new_explosion_sparks = []
                for e_spark in spark["explosion_sparks"]:
                    if e_spark["distance_left"] > 0:
                        # Move explosion spark
                        e_spark["col"] += e_spark["dx"] / self.speed
                        e_spark["row"] += e_spark["dy"] / self.speed
                        e_spark["distance_left"] -= math.sqrt(e_spark["dx"]**2 + e_spark["dy"]**2) / self.speed
                        new_explosion_sparks.append(e_spark)
                spark["explosion_sparks"] = new_explosion_sparks

                # Keep spark alive if it still has active explosion sparks
                if spark["explosion_sparks"]:
                    new_sparks.append(spark)
        self.sparks = new_sparks

    def render_frame(self, frame_buffer):
        """Render sparks on the frame buffer."""
        for spark in self.sparks:
            if spark["phase"] == "falling":
                # Render falling spark
                idx = spark["row"] * self.n_cols + spark["col"]
                if idx < len(frame_buffer):
                    frame_buffer[idx] = self.colour
            elif spark["phase"] == "exploding":
                # Render explosion sparks
                for e_spark in spark["explosion_sparks"]:
                    explosion_col = int(e_spark["col"])
                    explosion_row = int(e_spark["row"])
                    idx = explosion_row * self.n_cols + explosion_col
                    if 0 <= idx < len(frame_buffer):
                        frame_buffer[idx] = self.colour

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

                # Create a frame buffer
                frame_buffer = [(0, 0, 0) for _ in range(length)]

                # Launch new sparks
                self.launch_spark()

                # Update sparks
                self.update_sparks()

                # Render sparks and explosions
                self.render_frame(frame_buffer)

                # Write the frame buffer to the channel
                for i, colour in enumerate(frame_buffer):
                    r, g, b = colour
                    channel.buffer[i] = (max(0, min(r, 1)), max(0, min(g, 1)), max(0, min(b, 1)))

                channel.dispatch()
            self.delay()

if __name__ == "__main__":
    a = Fireworks()()

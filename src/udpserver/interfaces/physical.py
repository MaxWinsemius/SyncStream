"""
@author Max Winsemius
@date 15-01-2022
"""

from . import common
import socket
import math
import time

# TODO: Implement this. It removes the capabilities of setting the framebuffer_update array and checks if the
# previous send_framebuffer send the same data as the currently sending one, and therefore skips sending
# specific leds.
OPTIMIZED_UDP = False
DEBUG_SEND_UDP_PRINT = False

class PhysicalInterface(common.Interface):
    def __init__(self, ip, port, length, PACKET_LENGTH, maxbr, invert = False, MAX_INDEX = 4095, BIT_SHIFT = 4):
        self.ip = ip
        self.port = port
        self.length = length
        self.invert = invert
        self.PACKET_LENGTH = PACKET_LENGTH
        self.MAX_INDEX = MAX_INDEX
        self.BIT_SHIFT = BIT_SHIFT
        self.BIT_MULT = int(2**BIT_SHIFT)
        self.maxbr = maxbr

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if length > MAX_INDEX:
            raise ValueError(f"Trying to create physical interface with {length + 1} leds, but only supports 4096 leds")

        self.framebuffer = [common.Clr() for i in range(length)]
        self.framebuffer_previous = [common.Clr() for i in range(length)]
        self.framebuffer_update = [True for i in range(length)]

    def send_udp_framebuffer(self):
        maxbytes = self.PACKET_LENGTH - self.PACKET_LENGTH % 3
        fb = self.get_and_update_udp_framebuffer()

        if DEBUG_SEND_UDP_PRINT:
            print(f"{self.ip}:{self.port} bytedata {fb}")

        if len(fb) == 0:
            return
        elif len(fb) < maxbytes:
            self.sock.sendto(fb, (self.ip, self.port))
        else:
            curstep = 0
            while (curstep * maxbytes < len(fb)):
                start = curstep * maxbytes
                end = min((curstep + 1) * maxbytes, len(fb))
                self.sock.sendto(fb[start:end], (self.ip, self.port))
                curstep += 1

    def get_and_update_udp_framebuffer(self):
        fb = bytes()

        for i in [k for k in range(self.length) if self.should_i_update_this_frame(k)]:
            c_index = i if not self.invert else self.length - 1 - i
            ir, il = i%self.BIT_MULT, i//self.BIT_MULT
            r, g, b = [int(x/(256/self.BIT_MULT)*self.maxbr/(self.BIT_MULT-1)) for x in self.framebuffer[c_index].get_tuple()]
            self.framebuffer_previous[c_index].deepcopy(self.framebuffer[c_index])

            fb += bytes([
                il,
                ir*self.BIT_MULT + r,
                g*self.BIT_MULT + b
            ])

        return fb

    def should_i_update_this_frame(self, index):
        c_index = index if not self.invert else self.length - 1 - index

        if not self.framebuffer_update[c_index]:
            return False

        if self.framebuffer_previous[c_index] == self.framebuffer[c_index]:
            return False

        return True

    def set_color_array(self, start, stop, clr):
        self.check_start_stop_range(start, stop, len(clr))

        for i in range(len(clr)):
            self.framebuffer[start + i] = clr[i]

    def set_rgb_array(self, start, stop, rgb):
        self.check_start_stop_range(start, stop, len(rgb) / 3)

        for i in range(start, stop):
            j = (i - start) * 3
            r, g, b = rgb[j:j + 3]
            self.framebuffer[i] = common.Clr(r, g, b)

    def set_led(self, index, color):
        self.framebuffer[index] = color

    def set_led_rgb(self, index, r, g, b):
        self.set_led(index, common.Clr(r, g, b))

    def add_updating_range(self, start, stop):
        self.set_updating_range(start, stop, True)

    def remove_updating_range(self, start, stop):
        self.set_updating_range(start, stop, False)

    def set_updating_range(self, start, stop, update):
        self.check_start_stop_range(start, stop, stop - start)

        for i in range(start, stop):
            self.framebuffer_update[i] = update

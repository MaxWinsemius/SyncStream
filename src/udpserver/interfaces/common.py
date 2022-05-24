"""
@author Max Winsemius
@date 15-01-2022
"""

class InterfaceStartStopRangeException(Exception):
    pass

class Clr():
    def __init__(self, r = 0, g = 0, b = 0):
        self.r = r
        self.g = g
        self.b = b

    def __setattr__(self, name, value):
        if name in ["r", "g", "b"]:
            if not 0 <= value < 256:
                value = 0
        super().__setattr__(name, value)

    def __str__(self):
        return f"Clr(rgb=({self.r}, {self.g}, {self.b}))"

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Clr(int(self.r * other), int(self.g * other), int(self.b * other))

        if isinstance(other, Clr):
            return Clr(int(self.r * other.r), int(self.g * other.g), int(self.b * other.b))

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Clr(int(self.r + other), int(self.g + other), int(self.b + other))

        if isinstance(other, Clr):
            return Clr(int(self.r + other.r), int(self.g + other.g), int(self.b + other.b))

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Clr(int(self.r - other), int(self.g - other), int(self.b - other))

        if isinstance(other, Clr):
            return Clr(int(self.r - other.r), int(self.g - other.g), int(self.b - other.b))

    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b

    def __repr__(self):
        return self.__str__()

    def absint(self):
        return Clr(int(abs(self.r)), int(abs(self.g)), int(abs(self.b)))

    def deepcopy(self, other):
        self.r = other.r
        self.g = other.g
        self.b = other.b

    def get_tuple(self):
        return self.r, self.g, self.b

class Interface():
    def check_start_stop_range(self, start, stop, length):
        if start >= stop:
            raise InterfaceStartStopRangeException("Start is bigger than stop")

        if stop > self.length:
            raise InterfaceStartStopRangeException("Start is bigger than length")

        if stop - start != length:
            raise InterfaceStartStopRangeException("Difference between start and stop are not as big as the array length")

    def send_udp_framebuffer(self):
        """Sends the current framebuffer to the interface"""
        pass

    def set_color_array(self, start, stop, color_array):
        """Sets the led colors in bulk"""
        pass

    def set_rgb_array(self, start, stop, rgb_array):
        """Sets the led colors in bulk using seperate rgb values. Requires `(stop - start) % 3 = 0`"""
        pass

    def set_led(self, index, color):
        """Sets the color of the specified LED"""
        pass

    def set_led_rgb(self, index, r, g, b):
        """Sets the color of the speficied LED with seperate rgb values"""
        pass

    def add_updating_range(self, start, stop):
        """Adds a range of the framebuffer to update. Also seen as unfreezing a range"""
        pass

    def remove_updating_range(self, start, stop):
        """Remove a range of the framebuffer to update. Also seen as freezing a range"""
        pass

    def set_updating_range(self, start, stop, update):
        """Sets a range of the framebuffer to update or not"""
        pass

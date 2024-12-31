"""
@author Max Winsemius
@date 15-01-2022
"""

from . import common


class VirtualInterfaceOutOfBoundsException(Exception):
    pass


class VirtualInterface(common.Interface):
    def __init__(self):
        self.children = []  # No children yet

    def get_child_at_index(self, index):
        """Finds the child that has the led at this index"""

        for child in self.children:
            if child.start <= index < child.stop:
                return child

        raise VirtualInterfaceOutOfBoundsException(
            f"Tried to get child of framebuffer index {index} whilst Virtual" +
            f" Interface has length {self.length}.")

    def get_children_over_range(self, start, stop):
        """Finds the children that have the leds over the range of indices.
        Note that stop is exclusive, as if you are
        setting an array[start:stop]"""

        children = []

        for child in self.children:
            if child.stop > start and child.start < stop:
                children.append(child)

        return children

    def append_interface(self, interface):
        """Appends the given interface to this virtual interface, also checks
        if the new interface has this (self) as part of its children either,
        to prevent loops."""
        self.insert_interface(interface, self.length)

    def insert_interface(self, interface, index=0):
        """Inserts the given interface tot his virtual interface, and also
        checks if the new interface has this (Self) as part of its childeren
        either, to prevent loops."""
        # TODO: check to prevent self-loops

        # Insert in between two older interfaces
        if (len(self.children) > index):
            interface.start = self.children[index].start
            interface.stop = interface.start + interface.length

            for i in range(index, len(self.children)):
                self.children[i].start += interface.length
                self.children[i].stop += interface.length

            self.children.insert(index, interface)

        # Index is bigger than amount of children - 1
        else:
            interface.start = self.length
            interface.stop = interface.start + interface.length
            self.children.append(interface)

    def get_interfaces(self):
        return self.children

    def remove_interface(self, index):
        """removes the interface at the given index, if it exists"""

        if index < 0:
            raise ValueError(
                "Trying to remove negative index from Virtual Interface")

        for child in self.children[index + 1:]:
            child.start -= self.children.length
            child.stop -= self.children.length

        self.children[index].start = 0
        self.children[index].stop = self.children[index].length
        return self.children.pop(index)

    # common.Interface methods #

    @property
    def framebuffer(self):
        fb = []
        for child in self.children:
            fb.extend(child.framebuffer)
        return fb

    @property
    def length(self):
        length = 0
        for child in self.children:
            length += child.length
        return length

    def send_udp_framebuffer(self):
        for child in self.children:
            # First propagate the current framebuffer to the child
            # UNCOMMENTED since the framebuffer of the virtual interface is
            # not set at this moment in time, since when setting the color, it
            # can directly be propagated to the children
            # child.set_color_array(child.start, child.stop,
            #                       self.framebuffer[child.start:child.stop])

            # Second make the child send the framebuffer
            child.send_udp_framebuffer()

    def set_color_array(self, start, stop, color_array):
        self.check_start_stop_range(start, stop, len(color_array))

        children = self.get_children_over_range(start, stop)

        for child in children:
            # ca_start = index in color_array where the current child starts
            #            reading from
            # child_start = start index in child framebuffer where subsection
            #               of color_array is mapped to
            # ca_stop = index in color_array where the current child stops
            #           reading from
            # child_stop = stop index in child framebuffer where the subsection
            #              from the color_array is mapped to
            ca_start    = max(0,                    child.start - start)
            ca_stop     = min(child.stop - start,   len(color_array))
            child_start = max(start - child.start,  0)
            child_stop  = min(child.length,         stop - child.start)

            child.set_color_array(child_start, child_stop,
                                  color_array[ca_start:ca_stop])

    def set_rgb_array(self, start, stop, rgb):
        self.check_start_stop_range(start, stop, len(rgb) / 3)
        self.set_color_array(
            start,
            stop,
            [common.Clr(r, g, b)
                for r, g, b in [rgb[i:i+3] for i in range(0, len(rgb), 3)]])
        # wow such beautiful much python code

    def set_led(self, index, color):
        child = self.get_child_at_index(index)
        child.set_led(index - child.start, color)

    def set_led_rgb(self, index, r, g, b):
        self.set_led(index, common.Clr(r, g, b))

    def add_updating_range(self, start, stop):
        self.set_updating_range(start, stop, True)

    def remove_updating_range(self, start, stop):
        self.set_updating_range(start, stop, False)

    def set_updating_range(self, start, stop, update):
        self.check_start_stop_range(start, stop, stop - start)

        children = self.get_children_over_range(start, stop)

        for child in children:
            # child_start = start index in child framebuffer where subsection
            #               of color_array is mapped to
            # child_stop = stop index in child framebuffer where the subsection
            #              from the color_array is mapped to
            child_start = max(start - child.start, 0)
            child_stop  = min(child.length, stop - child.start)
            child.set_updating_range(child_start, child_stop, update)

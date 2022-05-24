from math import pi

class SeinpaalMixin:
    def get_index(self, channel, row, phi):
        n = row*channel.ringsize
        n += phi/2/pi*channel.ringsize
        n = max(min(n, channel.length), 0)
        nr = round(n)
        return nr, (1-abs(nr-n))**3
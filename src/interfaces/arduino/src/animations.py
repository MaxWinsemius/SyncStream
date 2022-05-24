import colorsys
from time import sleep
from math import sin, pi

#%% Helpers
hsv2rgb = lambda h,s,v: tuple(int(x * 15) for x in colorsys.hsv_to_rgb(h,s,v))

def cycle(arr, s=1):
    def _cycle0(arr): return [*arr[1:], arr[0]]
    def _cycle1(arr): return [arr[-1], *arr[:-1]]
    for _ in range(abs(s)): 
        if s>0: arr = _cycle0(arr)
        else:   arr = _cycle1(arr)
    return arr

#%% Animations
def regenboog(beunding, N, speed=1, dt=0.02, duration=30):
    Nsteps = int(duration//dt)

    buffer = [(x*1.0/N, 1, 1) for x in range(N)]

    for _ in range(Nsteps):
        for i, val in enumerate(buffer):
            beunding.setLed(i, hsv2rgb(*val))
        beunding.send()

        buffer = cycle(buffer, speed)

        sleep(dt)

def sinus(beunding, N, speed=1, dt=0.02, duration=30, colour=(15,15,15)):
    Nsteps = int(duration//dt)

    period = []
    for i in range(32):
        val = [c*sin(pi*i/32) for c in colour]
        val = [int(abs(c)) for c in val]
        period.append(val)

    for _ in range(Nsteps//len(period)):
        for col in period:
            for i in range(N):
                beunding.setLed(i, col)
            beunding.send()
            
            sleep(dt)

def set_colour(beunding, N, colour=(0,0,0)):
    for i in range(N):
        beunding.setLed(i, colour)
    beunding.send()


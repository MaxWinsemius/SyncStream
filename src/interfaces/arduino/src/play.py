from UDPStreamer import beunding
from animations import regenboog, sinus, set_colour
hor = beunding("10.0.0.91", 8888, 320, 4095)

sinus(hor, 46, colour=(15,0,0))
# regenboog(hor, 46, speed=3)
# set_colour(hor, 205, colour=(1,0,1))


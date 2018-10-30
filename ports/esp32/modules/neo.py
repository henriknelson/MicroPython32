from neopixel import NeoPixel
from machine import Pin

class Neo:
	def __init__(self,pin_nr):
		self.neo = NeoPixel(Pin(13),1)

	def set_color(self,r,g,b):
		self.neo[0] = (r,g,b)
		self.neo.write()



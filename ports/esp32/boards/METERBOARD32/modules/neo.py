from neopixel import NeoPixel
from machine import Pin
import time

class Neo:
	"""Wrapper for the NeoPixel class, creating a nicer interface for users working with NeoPixels"""

	def __init__(self,pin_nr):
		"""The constructor accepts a pin number to a pin that is connected to a NeoPixel"""
		self.neo = NeoPixel(Pin(13),1)

	def set_color(self,r,g,b):
		"""Set the NeoPixels color to the given RGB value"""
		self.neo[0] = (r,g,b)
		self.neo.write()

	def purple(self):
		self.set_color(128,0,128)

	def pulse(self,delay=100):
		"""Makes the NeoPixel pulse in different colors"""
		for index in range(0,2):
			i = 0
			while i<255:
				curr = list(self.neo[0])
				curr[index] = i
				self.neo[0] = curr
				time.sleep_ms(delay)
				self.neo.write()
				i+=1
			while i>255:
				curr = list(self.neo[0])
				curr[index] = i
				self.neo[0] = curr
				time.sleep_ms(delay)
				self.neo.write()
				i-=1

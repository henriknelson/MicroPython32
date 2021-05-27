from neopixel import NeoPixel
from machine import Pin, Timer
import time

class Neo:
	"""Wrapper for the NeoPixel class, creating a nicer interface for users working with NeoPixels"""

	def __init__(self,pin_nr):
		"""The constructor accepts a pin number to a pin that is connected to a NeoPixel"""
		self.neo = NeoPixel(Pin(13),1)
		self._siren_timer=Timer(0)
		self._siren_state=True

	def set_color(self,r,g,b):
		"""Set the NeoPixels color to the given RGB value"""
		self.neo[0] = (r,g,b)
		self.neo.write()

	def purple(self):
		self.set_color(128,0,128)


	def red(self):
		self.set_color(255,0,0)

	def green(self):
		self.set_color(0,255,0)

	def blue(self):
		self.set_color(0,0,255)

	def siren(self, sleep_time=450):
		def tick(input):
			self._siren_state=not self._siren_state
			if self._siren_state:
				self.blue()
			else:
				self.red()
		if sleep_time > 0:
			self._siren_timer.init(period=sleep_time, mode=Timer.PERIODIC, callback=tick)
		else:
			self._siren_timer.init()

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

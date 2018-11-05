from neopixel import NeoPixel
from machine import Pin
import time

class Neo:

	def __init__(self,pin_nr):
		self.neo = NeoPixel(Pin(13),1)

	def set_color(self,r,g,b):
		self.neo[0] = (r,g,b)
		self.neo.write()

	def pulse(self,delay=100):
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
	


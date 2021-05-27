import io
import machine
from machine import UART
import time
import ubinascii
import urequests
import ujson
from pprint import pprint
import sys
import uasyncio as asyncio
from network import WLAN
import network
import traceback
from machine import WDT

class MeterReader:

	def __init__(self, pin_nr):
		self._uart = UART(2, 115200, rx=pin_nr)
		self._uart.init(txbuf=1024, rxbuf=1024, timeout=11, timeout_char=11)
		self._sreader = asyncio.StreamReader(self._uart)
		self._request_url="https://api.cliffords.nu"
		self._wlan = network.WLAN(network.STA_IF)
		#self._wdt = WDT(timeout=20000)
		self._id = 0

	def connect(self):
		if not self._wlan.isconnected():
			self._wlan.active(True)
			self._wlan.connect("cliffords", "bluecompanysoldsleep")
			print("Connecting to WiFi..", end="")
			counter = 0
			while not self._wlan.isconnected():
				if counter > 5:
					raise Exception("Could not connect to wifi!")
				print("..",  end="")
				time.sleep(1)
				counter = counter + 1
			print("")
			print("Connected to WiFi:", self._wlan.ifconfig())

	def inc_id(self):
		self._id = self._id + 1
		return self._id

	def upload(self, hex_data):
		print("Uploading values to server:")
		payload = ujson.dumps({"jsonrpc": "2.0", "method": "push_aidon_values", "params": {"meter_values": hex_data}, "id": self.inc_id() })
		pprint(payload)
                self.connect()
		response=urequests.post(self._request_url, headers={'Content-Type':'application/json'}, data=payload)
		response.close()
		print("Upload done!")

	def reset_uart(self):
		print("Resetting UART..")
		data = self._uart.read(1)
		while data != None:
			data = self._uart.read(100)
			print("Reset UART loop")
		print("Reset of UART complete!")

	async def receive(self):
		while True:
			#self._wdt.feed()
			print("Receiving..")
			data = await self._sreader.read(337)
			print("Byte data received:")
			hex_data=ubinascii.hexlify(data)
			if len(data) == 337 and data[0] == 0x7e and data[-1] == 0x7e:
				print("A complete value package was received")
				self.upload(hex_data)
				print("Receive done!")

	def set_global_exception(self, loop):
		def handle_exception(loop, context):
			import sys
			sys.print_exception(context[exception])
			sys.exit()
		loop.set_exception_handler(handle_exception)

	def run(self):
		while True:
			try:
				print("Starting WiFi connection..")
				self.connect()
				print("Starting reading loop..")
				self.reset_uart()
				loop=asyncio.get_event_loop()
				self.set_global_exception(loop)
				loop.create_task(self.receive())
				loop.run_forever()
			except Exception as e:
				print("Exception in run()")
				import sys
				sys.print_exception(e)
				loop=asyncio.new_event_loop()


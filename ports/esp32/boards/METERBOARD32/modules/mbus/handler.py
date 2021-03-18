from mbus.device import MBusDevice
from mbus.record import ValueRecord
from mbus.uart import MBusUART
from machine import RTC
import ubinascii
import ujson
import time
import uasyncio_fast as asyncio

class MBusHandler:
	"""MBus emulator library worker\n~~~~~~~~~~~~~~~~~~~~~\n\nThis class keeps track of one or more emulated MBus devices.\nClients are provided with an interface to add new devices, either as objects or in serialized form.\nIt also acts as a worker thread, continuously polling the MBUS UART for communication from a connected MBus master.\nWhen a MBus master request has been received, it is responsible for passing it on to the emulated devices, and sending back their responses to the master.\n"""
	def __init__(self,baudrate=2400,timeout=350,debug=False):
		self.mbus_uart = MBusUART(baudrate=baudrate,timeout=timeout,callback=self.handle_incoming_telegram,debug=debug)
		self.devices = {}
		self.loop = asyncio.get_event_loop()
		self.loop.create_task(self.mbus_uart.read_telegram())
		self.loop.create_task(self.update_devices())
		self.rtc = RTC()

	def parse_devices(self):
		"""Adds one or more devices that has been described in serialized format, from a file"""
		meter_file = open(".config/meter_config.json")
		meter_file_json = meter_file.read()
		meter_object = ujson.loads(meter_file_json)
		for meter in meter_object:
			mbus_meter = MBusDevice(meter["PrimaryAddress"],meter["MeterId"],meter["ManufacturerId"],meter["MeterType"])
			for record in meter["DataRecords"]:
				dib = ubinascii.unhexlify(record["dib"])
				vib = ubinascii.unhexlify(record["vib"])
				data = ubinascii.unhexlify(record["data"])
				mbus_record = ValueRecord(dib,vib,data)
				mbus_meter.add_record(mbus_record)
			mbus_meter.seal()
			self.add_device(mbus_meter)
		meter_file.close()

	def add_device(self, device):
		"""Adds a single device to the internal list of devices to keep track of"""
		self.log("Device {} added [primary_address: {}, meter_type: {}, manufacturer: {}, records: {}]"
			  .format(device.get_secondary_address(),device.get_primary_address(),device.get_type(),device.get_manufacturer_id(),len(device._records)))
		self.devices[device.get_primary_address()] = device

    	def get_time(self):
        	return "%02u:%02u:%02u (%d)" % self.rtc.datetime()[4:8]

    	def log(self, message):
        	print("[{}][debug   ] {}".format(self.get_time(),message))

	def start(self):
		"""Starts the communication loop"""
		print("Initializing MBus handler..")
		self.parse_devices()
		self.loop.run_forever()

	async def update_devices(self):
		while True:
			await asyncio.sleep(60*60)
			for device in self.devices.values():
				device.update()

	def handle_incoming_telegram(self,telegram,ticks):
		"""Called whenever a new MBus master request has been received.\nParses the request and ensures the correct responses from the tracked devices are collected and sent back.\n"""
		if telegram[0] == 0x10:
			# SND_NKE
			if telegram[1] == 0x40:
				# If broadcast to 0xfd, deselect the currently selected device
				if telegram[2] == 0xfd:
					list(map(lambda device: device.deselect(),self.devices.values()))
				# If broadcast to all devices on bus, have them reply or indicate collision
				elif telegram[2] == 0xfe:
					#map(lambda device: device.select(),self.devices.values())
					no_of_devices = len(list(self.devices.values()))
					if no_of_devices >= 2:
						self.mbus_uart.send_collision()
					elif no_of_devices == 1:
						self.mbus_uart.send_ack()
				# If wanting to select a specific device via primary address
				elif telegram[2] in self.devices.keys():
					self.mbus_uart.send_ack()
			# REQ_UD2
			elif ((telegram[1] == 0x5b) or (telegram[1] == 0x7b)):
				# If broadcast to 0xFD (selected devices)..
				if telegram[2] == 0xfd:
					devices_found = [device for device in self.devices.values() if device.is_selected()]
					no_of_devices = len(devices_found)
					if no_of_devices >=2:
						self.mbus_uart.send_collision()
					elif no_of_devices == 1:
						device = devices_found[0]
						resp_bytes = ubinascii.unhexlify(device.get_latest_values())
						self.mbus_uart.send_telegram(resp_bytes,ticks)
				# If targetting a specific device via primary address					
				elif (telegram[2] in self.devices.keys()):
					device = self.devices[telegram[2]]
					resp_bytes = ubinascii.unhexlify(device.get_latest_values())
					self.mbus_uart.send_telegram(resp_bytes,ticks)						
		elif telegram[0] == 0x68:
			# SND_UD
			if ((telegram[4] == 0x53) or (telegram[4] == 0x73)):
				if ((telegram[5] == 0xfd) and (telegram[6] == 0x52)):
					search_bytes = list(telegram[7:11])
					search_bytes.reverse()
					search_string = "".join(['{0:0{1}x}'.format(b,2) for b in search_bytes])
					self.log("searching with string {}".format(search_string))
					devices_found = [device for device in self.devices.values() if device.matches_secondary_address(search_string)]
					devices_not_found = [device for device in self.devices.values() if device not in devices_found]
					list(map(lambda device: device.select(),devices_found))
					list(map(lambda device: device.deselect(),devices_not_found))
					if(len(devices_found) >= 2):
						self.log("multiple devices found for search string {}".format(search_string))
						for device in devices_found:
							self.mbus_uart.send_ack()
					elif(len(devices_found) == 1):
						device = devices_found[0]
						self.log("one device found for search string {}".format(search_string))
						self.mbus_uart.send_ack()
					#self.mbus_uart.send_telegram(resp_bytes,ticks)

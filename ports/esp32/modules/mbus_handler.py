from mbus_device import MBusDevice
from mbus_record import MBusValueRecord
from mbus_uart import MBusUART
import ubinascii
import ujson
import time
import uasyncio as asyncio

class MBusHandler:

    def __init__(self,baudrate=2400,timeout=350,debug=False):
        self.devices = {}
        self.mbus_uart = MBusUART(baudrate=baudrate,timeout=timeout,callback=self.handle_incoming_telegram,debug=debug)
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.mbus_uart.read_telegram())
        self.loop.create_task(self.update_devices())

    def parse_devices(self):
        meter_file = open(".config/meter_config.json")
        meter_file_json = meter_file.read()
        meter_object = ujson.loads(meter_file_json)
        for meter in meter_object:
            mbus_meter = MBusDevice(meter["PrimaryAddress"],meter["MeterId"],meter["ManufacturerId"],meter["MeterType"])
            for record in meter["DataRecords"]:
                dib = ubinascii.unhexlify(record["dib"])
                vib = ubinascii.unhexlify(record["vib"])
                data = ubinascii.unhexlify(record["data"])
                mbus_record = MBusValueRecord(dib,vib,data)
                mbus_meter.add_record(mbus_record)
            mbus_meter.seal()
            self.add_device(mbus_meter)
        meter_file.close()

    def add_device(self, device):
        print("Device {} added [primary_address: {}, meter_type: {}, manufacturer: {}, records: {}]"
              .format(device.get_secondary_address(),device.get_primary_address(),device.get_type(),device.get_manufacturer_id(),len(device._records)))
        self.devices[device.get_primary_address()] = device

    def start(self):
        print("Initializing MBus handler..")
        self.parse_devices()
        self.loop.run_forever()

    async def update_devices(self):
        while True:
            await asyncio.sleep(60*60)
            for device in self.devices.values():
                device.update()

    def handle_incoming_telegram(self,telegram,ticks):
         if (telegram[1] == 0x40) and ((telegram[2] == 0xfe) or (telegram[2] == 0xfd) or (telegram[2] in self.devices.keys())):
            self.mbus_uart.send_telegram(bytearray([0xE5]),ticks)
         elif ((telegram[1] == 0x5b) or (telegram[1] == 0x7b)) and (telegram[2] in self.devices.keys()):
            device = self.devices[telegram[2]]
            resp_bytes = ubinascii.unhexlify(device.get_latest_values())
            self.mbus_uart.send_telegram(resp_bytes,ticks)

from mbus_device import MBusDevice
from mbus_record import MBusValueRecord
from mbus_uart import MBusUART
import ubinascii
import ujson

class MBusHandler:

    def __init__(self):
        self.mbus_uart = MBusUART()
        self.devices = {}

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
            self.add_device(mbus_meter)
        meter_file.close()

    def add_device(self, device):
        print("Device {} added [primary_address: {}, meter_type: {}, manufacturer: {}, records: {}"
              .format(device.get_secondary_address(),device.get_primary_address(),device.get_type(),device.get_manufacturer_id(),len(device._value_records)))
        self.devices[device.get_primary_address()] = device

    def start(self):
        print("Starting handler..")
        self.devices = {}
        self.parse_devices()
        self.run()

    def run(self):
        while True:
            mbus_message = self.mbus_uart.read_telegram()
            if (mbus_message[1] == 0x40) and ((mbus_message[2] == 0xfe) or (mbus_message[2] == 0xfd) or (mbus_message[2] in self.devices.keys())):
                self.mbus_uart.send_telegram(bytearray([0xE5]))
            elif ((mbus_message[1] == 0x5b) or (mbus_message[1] == 0x7b)) and (mbus_message[2] in self.devices.keys()):
                device = self.devices[mbus_message[2]]
                resp_bytes = ubinascii.unhexlify(device.get_rsp_ud2())
                self.mbus_uart.send_telegram(resp_bytes)

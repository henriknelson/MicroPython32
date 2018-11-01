from machine import UART
import time
import ubinascii
import uasyncio as asyncio
from mbus_reader import MBusReader

class MBusUART:

    def __init__(self,baudrate=2400,timeout=350,callback=lambda x:print(x),debug=False):
        self.callback = callback
        self.uart = UART(2, baudrate)
        self.uart.init(baudrate,bits=8,parity=0,stop=1,timeout=timeout)
        self.mbus_reader = MBusReader(self.uart)
        self.mbus_reader.set_debug(debug)

    def get_time(self):
        return "%04u-%02u-%02u %02u:%02u:%02u" % time.localtime()[0:6]

    async def read_telegram(self):
        while True:
            telegram = await self.mbus_reader.read_telegram() 
            if telegram != None:
		ticks = time.ticks_ms()
                self.log_incoming(telegram)
                self.callback(telegram,ticks)
            await asyncio.sleep(0)

    def log_incoming(self, data_bytes):
        print("[{}][master <] - {}".format(self.get_time(),ubinascii.hexlify(data_bytes, "-")))

    def log_outgoing(self, data_bytes):
        print("[{}][slave  >] - {}".format(self.get_time(),ubinascii.hexlify(data_bytes, "-")))

    def log_echo(self, data_bytes):
        print("[{}][echo    ] - {}".format(self.get_time(),ubinascii.hexlify(data_bytes, "-")))

    def send_telegram(self, data, ticks):
        len_data = len(data)
        send_ticks = time.ticks_ms()
        time_diff = send_ticks - ticks
        self.uart.write(data)
        send_ticks = time.ticks_ms()
        self.log_outgoing(data)
        time_diff = send_ticks - ticks
        # Since the MBus transceiver echoes all transmitted data on the RX line..
        # .. we have to get rid of the echoed data before continuing reading
        duplicated_bytes = bytearray([])
        while (len(duplicated_bytes) != len_data):
            read_bytes = self.uart.read(len_data - len(duplicated_bytes))
            if read_bytes == None:
                continue
            duplicated_bytes.extend(read_bytes)
        self.log_echo(duplicated_bytes)
        print("The reply was sent to the master after {} milliseconds".format(time_diff))
        print("\r\n")


from machine import UART, RTC
from mbus.reader import MBusReader
import time
import ubinascii
import uasyncio_fast as asyncio

class MBusUART:
    """Wrapper for a HW UART connected to an MBus bus (via a TSS721 IC).\nProvides the user with a nice interface for reading/writing, and also provides the possibility to signal collisions on the bus.\n"""
    def __init__(self,baudrate=2400,timeout=350,callback=lambda x:print(x),debug=False):
        self.callback = callback
        self.uart = UART(2, baudrate)
        self.uart.init(baudrate,bits=8,parity=0,stop=1,timeout=timeout)
        self.mbus_reader = MBusReader(self.uart)
        self.mbus_reader.set_debug(debug)
        self.rtc = RTC()

    def set_parity(self,parity):
        self.uart.init(parity=parity)

    def send_collision(self):
        self.log_debug_string("debug","sent collision")
        self.set_parity(1)
        self.send_telegram(bytearray([0x00]))	
        self.set_parity(0)

    def send_ack(self):
        self.log_debug_string("debug","sent ACK")
        self.send_telegram(bytearray([0xE5]))	

    def get_time(self):
        return "%02u:%02u:%02u (%d)" % self.rtc.datetime()[4:8]

    async def read_telegram(self):
        while True:
            telegram = await self.mbus_reader.read_telegram() 
            if telegram != None:
                ticks = time.ticks_ms()
                self.log_incoming(telegram)
                self.callback(telegram,ticks)
            await asyncio.sleep(0)

    def log_incoming(self, data_bytes):
        print("[{}][master <] - {}".format(self.get_time(),ubinascii.hexlify(data_bytes)))

    def log_outgoing(self, data_bytes):
        print("[{}][slave  >] - {}".format(self.get_time(),ubinascii.hexlify(data_bytes)))

    def log_debug(self,name,data_bytes):
        print("[{}][{}   ] - {}".format(self.get_time(),name, ubinascii.hexlify(data_bytes)))

    def log_debug_string(self,name,debug_string):
        print("[{}][{}   ] - {}".format(self.get_time(),name, debug_string))

    def send_telegram(self, data, ticks=None):
        len_data = len(data)
        if ticks:
           send_ticks = time.ticks_ms()
           time_diff = send_ticks - ticks
        self.uart.write(data)
        if ticks:
           send_ticks = time.ticks_ms()
           time_diff = send_ticks - ticks
        self.log_outgoing(data)
        # Since the MBus transceiver echoes all transmitted data on the RX line..
        # .. we have to get rid of the echoed data before continuing reading
        duplicated_bytes = bytearray([])
        while (len(duplicated_bytes) != len_data):
            read_bytes = self.uart.read(len_data - len(duplicated_bytes))
            if read_bytes == None:
                continue
            duplicated_bytes.extend(read_bytes)
        self.log_debug("echo  ",duplicated_bytes)
        if ticks:
            self.log_debug_string("debug","The reply was sent to the master after {} milliseconds".format(time_diff))
        print("\r\n")


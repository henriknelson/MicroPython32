from machine import UART
import time
import ubinascii

class MBusUART:

    def __init__(self,baudrate=2400):
        self.uart = UART(2, baudrate)
        self.uart.init(baudrate=baudrate,bits=8,parity=0,stop=1,timeout_char=0)

    def get_time(self):
        return "%04u-%02u-%02u %02u:%02u:%02u" % time.localtime()[0:6]

    def read_telegram(self):
        while True:
            # Read one byte..
            read_bytes = self.uart.read(1)
            if (read_bytes != None) and (len(read_bytes) > 0):
                # .. and perform branch jump depending on message type
                if read_bytes[0] == 0x10:
                    return self.handle_short_message()
                elif read_bytes[0] == 0x68:
                    return self.handle_long_message()

    def handle_short_message(self):
        append_bytes = self.uart.read(4)
        if (append_bytes != None) and (len(append_bytes) == 4):
            ticks = time.ticks_ms()
            mbus_message = bytearray([0x10]) + append_bytes
            self.log_incoming(ubinascii.hexlify(mbus_message, "-"))
            return mbus_message,ticks

    def handle_long_message(self):
        header_bytes = self.uart.read(3)
        if (header_bytes != None) and (len(header_bytes) == 3):
            mbus_message_start = bytearray([0x68]) + header_bytes
            length = mbus_message_start[1]
            append_bytes = self.uart.read(length + 2)
            if (append_bytes != None) and (len(append_bytes) > 0):
                ticks = time.ticks_ms()
                mbus_message = mbus_message_start + append_bytes
                self.log_incoming(ubinascii.hexlify(mbus_message, "-"))
                return mbus_message,ticks

    def log_incoming(self, incoming_bytes):
        print("[{}][master >] - {}".format(self.get_time(),incoming_bytes))

    def log_outgoing(self, outgoing_bytes):
        print("[{}][slave  <] - {}".format(self.get_time(),outgoing_bytes))

    def send_telegram(self, data, ticks):
        self.log_outgoing(ubinascii.hexlify(data, "-"))
        len_data = len(data)
        send_ticks = time.ticks_ms()
        print("sending reply after {} ms".format(send_ticks-ticks))
        self.uart.write(data)
        # Since the MBus transceiver echoes all transmitted data on the RX line..
        # .. we have to get rid of the echoed data before continuing reading
        duplicated_bytes = bytearray([])
        while True:
            read_byte = self.uart.read(1)
            if read_byte == None:
                continue
            duplicated_bytes = read_byte + duplicated_bytes
            if (len(duplicated_bytes) == len_data):
                break

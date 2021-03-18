import uasyncio_fast as asyncio
from uasyncio_fast.core import *
import ubinascii

class MBusReader(asyncio.StreamReader):
    """StreamReader descendant that tries to read a MBus telegram on an MBus bus"""

    def __init__(self, polls, ios=None):
        super().__init__(polls,ios)
        if ios is None:
            ios = polls
        self.polls = polls
        self.ios = ios

    def __repr__(self):
        return "<MBusReader %r %r>" % (self.polls, self.ios)

    def set_debug(self,debug):
        asyncio.set_debug(debug)

    def read_telegram(self):
        if DEBUG and __debug__:
            log.debug("MBusReader.read_telegram()")
        buf = bytearray(b'')
        while True:
            yield IORead(self.polls)
            res = self.ios.read_mbus_telegram()
            assert res is not None
            if not res:
                break
            if DEBUG and __debug__:
                print("res: {}".format(ubinascii.hexlify(bytearray(res),"-")))
            buf += bytearray(res)
            if (len(buf) >= 2):
                if ((buf[0] == 0x10) and (len(buf) == 5) and (buf[-1] == 0x16)):
                    break
                elif ((buf[0] == 0x68) and (len(buf) == (buf[1] + 6)) and (buf[(buf[1] + 5)] == 0x16)):
                    if(len(buf) > (buf[1] + 6)):
                       print("obviously we read too much")
                    buf = buf[0:(buf[1] + 6)]
                    break
                else:
                    buf = bytearray(b'')
                    print("WTF; {}".format(ubinascii.hexlify(buf,"-")))
        if DEBUG and __debug__:
            log.debug("MBusReader.read_telegram(): %s", buf)
        yield IOReadDone(self.polls)
        return buf

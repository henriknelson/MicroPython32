import uos
from flashbdev import bdev

def check_bootsec():
    buf = bytearray(bdev.SEC_SIZE)
    bdev.readblocks(0, buf)
    empty = True
    for b in buf:
        if b != 0xff:
            empty = False
            break
    if empty:
        return True
    fs_corrupted()

def fs_corrupted():
    import time
    while 1:
        print("""\
FAT filesystem appears to be corrupted. If you had important data there, you
may want to make a flash snapshot to try to recover it. Otherwise, perform
factory reprogramming of MicroPython firmware (completely erase flash, followed
by firmware programming).
""")
        time.sleep(3)

def setup():
    check_bootsec()
    print("Performing initial setup")
    uos.VfsFat.mkfs(bdev)
    vfs = uos.VfsFat(bdev)
    uos.mount(vfs, '/flash')
    uos.chdir('/flash')
    with open("boot.py", "w") as f:
        f.write("""\
# This file is executed on every boot (including wake-boot from deepsleep)
from network import WLAN
import esp
import time
import ntptime
import machine
esp.osdebug(None)
print("Welcome to MeterBus32")
print("---------------------")
wlan = WLAN()
wlan.active(True)
wlan.connect("Helan","Un0s245A!")
print("Connecting to WiFi..", end="")
while not wlan.isconnected():
    print(".",end="")
    time.sleep_ms(200)
print("")
print("Connected to WiFi:", wlan.ifconfig())
time.sleep(2)
ntptime.settime()
print("Current time set via NTP server to:", "%04u-%02u-%02u %02u:%02u:%02u" % time.localtime()[0:6])
import webrepl
webrepl.start()
""")
    with open("main.py", "w") as f2:
        f2.write("""\
# This file is executed after every boot)
from neo import Neo
from mbus_device import MBusDevice
from mbus_handler import MBusHandler
from mbus_record import MBusValueRecord

neo = Neo(13)
neo.set_color(255,0,0)
handler = MBusHandler()
handler.start()
""")
    uos.mkdir('/flash/.config')
    uos.chdir('/flash/.config')
    with open("meter_config.json", "w") as f3:
        f3.write("""\
[
  {
    "DataRecords": [
      {
        "dib": "02",
        "vib": "06",
        "data": "D204"
      }
    ],
    "MeterId": "14881488",
    "PrimaryAddress": 2,
    "MeterType": 4,
    "ManufacturerId": "HCN"
  }
]
""")
    return vfs

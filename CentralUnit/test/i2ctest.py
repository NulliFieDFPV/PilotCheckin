import smbus
import time

bus=smbus.SMBus(0)

while True:
    bus.write_byte_data(0x38, 0x00, 0x00)

    time.sleep(1)

    bus.write_byte_data(0x38, 0x00, 0xFF)

    time.sleep(1)

    bus.write_byte_data(0x38, 0x01, 0x00)

    time.sleep(1)

    bus.write_byte_data(0x38, 0x01, 0xFF)

    time.sleep(1)
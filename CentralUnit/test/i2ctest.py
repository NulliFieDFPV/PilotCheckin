import smbus
import time

bus=smbus.SMBus(0)

while True:
    bus.write_byte_data(0x38, 0x00, 0x00)

    time.sleep(1)

    bus.write_i2c_block_data(0x38, 0x09, [0xFF, 1,2,3,4,5,6,7])

    time.sleep(1)

    bus.write_byte_data(0x38, 0x01, 0x00)

    time.sleep(1)

    bus.write_byte_data(0x38, 0x02, 0xF0)

    time.sleep(1)
import smbus
import time
import struct

bus=smbus.SMBus(0)




def writeNumber2(value):
  strout = struct.pack('<i', value)
  for i in range(4):
    bus.write_byte(address, strout[i])
  return -1

def writeNumber(value):

    # assuming we have an arbitrary size integer passed in value
    for character in str(value): # convert into a string and iterate over it
        bus.write_byte(0x38, ord(character)) # send each char's ASCII encoding

    return -1
    bus.r
def readNumber():

    # I'm not familiar with the SMbus library, so you'll have to figure out how to
    # tell if any more bytes are available and when a transmission of integer bytes
    # is complete. For now, I'll use the boolean variable "bytes_available" to mean
    # "we are still transmitting a single value, one byte at a time"

    byte_list = []
    while bytes_available:
        # build list of bytes in an integer - assuming bytes are sent in the same
        # order they would be written. Ex: integer '123' is sent as '1', '2', '3'
        byte_list.append(bus.read_byte(address))

    # now recombine the list of bytes into a single string, then convert back into int
    number = int("".join([chr(byte) for byte in byte_list]))
    return number



while True:

    #try:
    writeNumber("hallo;")
    time.sleep(1)
    continue
    # except:
    print "fehler"
    bus=smbus.SMBus(0)
    continue

    """
    bus.write_byte_data(0x38, 0x00, 0x00)

    time.sleep(1)

    bus.write_i2c_block_data(0x38, 0x09, [0xFF, 1,2,3,4,5,6,7,8,9,10,11,12,13])

    c="hallo"

    time.sleep(1)

    #bus.write_byte_data(0x38, 0x02, ";".encode("hex"))
    """
    time.sleep(1)

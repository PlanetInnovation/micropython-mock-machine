# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Planet Innovation
# 436 Elgar Road, Box Hill, 3128, VIC, Australia
# Phone: +61 3 9945 7510
#
# The copyright to the computer program(s) herein is the property of
# Planet Innovation, Australia.
# The program(s) may be used and/or copied only with the written permission
# of Planet Innovation or in accordance with the terms and conditions
# stipulated in the agreement/contract under which the program(s) have been
# supplied.

"""
Mock machine module that can be used in unit tests to test drivers

Current:
    - I2C
    - SPI
    - Pin
    - ADC
"""

class MockI2C: 
    """
    Unittest support class for machine.I2C
    """

    def __init__(self, id=None, *, scl=None, sda=None , freq=400000):
        """
        Construct and return a new I2C object
        Initialise mock I2C with register values
        """

        self.register_values = {}

    # General methods
    def init(scl, sda, *, freq=400000):
        """
        Initialise the I2C bus
        """
        pass

    def deinit():
        """
        Turn off the I2C bus
        """
        pass

    def scan():
        """
        Scan all I2C addresses between 0x08 and 0x77 inclusive and return a list of those that respond.
        """
        pass

    # Standard bus operations
    def readfrom(addr, nbytes, stop=True,/):
        """
        Read nbytes from the peripheral specified by addr. 
        If stop is true then a STOP condition is generated at the end of the transfer.
        Returns a bytes object with the data read.
        """
        pass

    def readfrom_into(addr, bug, stop=True,/):
        """
        Read into buf from the peripheral specified by addr. 
        The number of bytes read will be the length of buf. 
        If stop is true then a STOP condition is generated at the end of the transfer.
        The method returns None.
        """
        pass

    def writeto(self, addr, buf, stop=True,/):
        """
        Write the bytes from buf to the peripheral specified by addr. 
        If a NACK is received following the write of a byte from buf then the remaining bytes are not sent. 
        If stop is true then a STOP condition is generated at the end of the transfer, even if a NACK is received. 
        The function returns the number of ACKs that were received.
        """
        pass

    # Memory operations
    def readfrom_mem(self, addr, memaddr, nbytes, *, addrsize=8):
        """
        Read nbytes from the peripheral specified by addr starting from the memory address specified by memaddr. 
        The argument addrsize specifies the address size in bits. Returns a bytes object with the data read.
        """
        if memaddr not in self.register_values:
            raise ValueError("Register not known")  # fixme: Which register
        if len(self.register_values[memaddr]) != nbytes:
            raise ValueError("Unexpected length")  # fixme: Improve error report
        return self.register_values[memaddr]

    def readfrom_mem_into(addr, memaddr, buf, *, addrsize=8):
        """
        Read into buf from the peripheral specified by addr starting from the memory address specified by memaddr. 
        The number of bytes read is the length of buf. The argument addrsize specifies the address size in bits
        The method returns None.
        """
        pass

    def writeto_mem(addr, memaddr, buf, *, addrsize=8):
        """
        Write buf to the peripheral specified by addr starting from the memory address specified by memaddr. 
        The argument addrsize specifies the address size in bits 
        The method returns None.
        """
        pass

class MockSPI:
    """
    Unittest support class for machine.SPI
    """

    def __init__(self, id=None):
        """
        Construct an SPI object on the given bus, id.
        """
        self.readbuf = b""

    # SPI Methods
    def init(self, baudrate=1000000, *, polarity=0, phase=0, bits=8, firstbit=None, sck=None, mosi=None, miso=None, pins=None):
        """
        Initialise the SPI bus with the given parameters
        """
        pass

    def deinit():
        """
        Turn off the SPI bus
        """
        pass

    def read(self, nbytes, write=0x00):
        """
        Read a number of bytes specified by nbytes while continuously writing the single byte given by write. 
        Returns a bytes object with the data that was read.
        """
        return self.readbuf[:nbytes]

    def readinto(buf, write=0x00):
        """
        Read into the buffer specified by buf while continuously writing the single byte given by write. 
        Returns None.
        """
        pass

    def write(buf):
        """
        Write the bytes contained in buf. 
        Returns None.
        """
        pass

    def write_readinto(write_buf, read_buf):
        """
        Write the bytes from write_buf while reading into read_buf. 
        The buffers can be the same or different, but both buffers must have the same length. 
        Returns None.
        """
        pass

class MockPin:
    """
    Unittest support class for machine.Pin
    Allows manual setting of input or output pin's value.
    Taken from radiata/src/firmware/test/mocks.py
    """

    IN = 0
    OUT = 1
    ALT = 2

    IRQ_RISING = 269549568
    IRQ_FALLING = 270598144

    def __init__(self, _, mode=0, pull=0):
        self._value = 0
        self._mode = mode
        self._pull = pull
        self._alt = None

    def init(self, mode=0, pull=0, alt=0):
        self._mode = mode
        self._pull = pull
        self._alt = alt

    def value(self, new_value=None):
        if new_value is not None:
            self._value = new_value
            return None
        return self._value

    def on(self):
        self._value = 1

    def off(self):
        self._value = 0

    def irq(self, *args, **kwargs):
        pass

    def mode(self):
        return self._mode

    def __call__(self, x=None):
        return self.value(x)

class MockADC:
    """
    Test support class for machine.ADC.
    Modified from radiata/src/firmware/test/mocks.py
    """

    def __init__(self, pin):
        self.pin = pin
        self.value_u16 = 0

    # Methods
    def init(*, sample_ns, atten):
        """
        Apply the given settings to the ADC. 
        Only those arguments that are specified will be changed.
        """
        pass

    def block():
        """
        Return the ADCBlock instance associated with this ADC object.
        """
        pass

    def read_u16(self):
        """
        Take an analog reading and return an integer in the range 0-65535. 
        The return value represents the raw reading taken by the ADC
        """
        return self.value_u16

    def read_uv():
        """
        Take an analog reading and return an integer value with units of microvolts. 
        It is up to the particular port whether or not this value is calibrated, and how calibration is done.
        """
        pass


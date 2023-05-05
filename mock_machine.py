# -*- coding: utf-8 -*-
#
# PI Background IP
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
Mock machine module that can be used in unit tests to test drivers.

Currently implements: ADC, I2C, Pin, SPI
"""

import errno

import micropython

# Not concerned about unused arguments in mocks
# pylint: disable=unused-argument


class I2CDevice:
    """
    A single I2C device added to a mock_machine.I2C bus.
    """

    def __init__(self, addr, i2c):
        self.addr = addr

        # Dict of buffers used for addressed operations
        self.register_values = {}

        # A buffer used for non-addressed reads
        self.readbuf = bytes()

        # Add self to I2C
        i2c.add_device(self)

    # Standard bus operations
    def readfrom(self, nbytes, stop=True):
        """
        Read nbytes from the peripheral.

        Returns a bytes object with the data read.
        """
        if len(self.readbuf) < nbytes:
            raise ValueError(f"Insufficient bytes to read {nbytes=} with readfrom()")
        buf = self.readbuf[:nbytes]
        return buf

    def readfrom_into(self, buf, stop=True):
        """
        Read into buf from the peripheral.

        The number of bytes read will be the length of buf.

        The method returns None.
        """
        if len(self.readbuf) < len(buf):
            raise ValueError(f"Insufficient bytes to read {len(buf)} with readfrom_into()")
        buf[:] = self.readbuf[: len(buf)]

    @staticmethod
    def writeto(buf, stop=True):
        """
        Write the bytes from buf to the peripheral.

        If a NACK is received following the write of a byte from buf then the remaining bytes are
        not sent.

        If `writeto` is required for a peripheral, then this function will need to be overridden
        with desired functionality. Otherwise this function defaults to ACK for all bytes.

        The function returns the number of ACKs that were received.
        """
        return len(buf)

    # Memory operations
    def readfrom_mem(self, memaddr, nbytes):
        """
        Read nbytes from the peripheral starting at memaddr.

        Returns a bytes object with the data read.
        """
        if memaddr not in self.register_values:
            raise IndexError(
                f"Unknown memory address {memaddr=}",
            )
        if len(self.register_values[memaddr]) < nbytes:
            raise ValueError(f"Insufficient bytes to read {nbytes=} from {memaddr=}")
        buf = self.register_values[memaddr][:nbytes]
        return buf

    def readfrom_mem_into(self, memaddr, buf):
        """
        Read into buf from the peripheral specified by addr, starting at memaddr.

        The number of bytes read is the length of buf. The argument addrsize specifies the address
        size in bits.

        The method returns None.
        """
        if memaddr not in self.register_values:
            raise IndexError(
                f"Unknown memory address {memaddr=:x}",
            )
        if len(self.register_values[memaddr]) < len(buf):
            raise ValueError(f"Insufficient bytes to read {len(buf)=} from {memaddr=}")
        buf[:] = self.register_values[memaddr][: len(buf)]

    def writeto_mem(self, memaddr, buf):
        """
        Write buf to the peripheral specified by addr, starting at memaddr.

        The number of bytes written is the length of buf. The argument addrsize specifies the
        address size in bits.

        The method returns None.
        """
        self.register_values[memaddr] = buf


class I2C:
    """
    Unittest support class for machine.I2C.
    """

    def __init__(
        self, *args, id=None, scl=None, sda=None, freq=400000
    ):  # pylint: disable=unused-argument,redefined-builtin
        """
        Construct a new I2C object.

        Initialise mock I2C with register values.
        """
        self.devices = {}

    # Device management methods
    def add_device(self, device):
        """
        Add I2CDevice at address I2CDevice.address.
        """
        if device.addr in self.devices:
            raise ValueError("Device with given address already on bus.")
        self.devices[device.addr] = device

    # General methods
    def init(self, scl, sda, *args, freq=400000):
        """
        Initialise the I2C bus.
        """

    def deinit(self):
        """
        Turn off the I2C bus.
        """

    def scan(self):
        """
        Scan I2C for responding devices.

        Scans all I2C addresses between 0x08 and 0x77 inclusive and return a list of those that
        respond.

        Returns a list of addresses that responded to the scan.
        """
        scan_list = []
        for addr in self.devices:
            if 0x08 <= addr <= 0x77:
                scan_list.append(addr)
        return scan_list

    # Standard bus operations
    def readfrom(self, addr, nbytes, stop=True):
        """
        Read nbytes from the peripheral specified by addr.

        If stop is true then a STOP condition is generated at the end of the transfer.

        Returns a bytes object with the data read.
        """
        if addr not in self.devices:
            raise OSError(errno.ENODEV)
        return self.devices[addr].readfrom(nbytes, stop)

    def readfrom_into(self, addr, buf, stop=True):
        """
        Read into buf from the peripheral specified by addr.

        The number of bytes read will be the length of buf. If stop is true then a STOP condition
        is generated at the end of the transfer.

        The method returns None.
        """
        if addr not in self.devices:
            raise OSError(errno.ENODEV)
        return self.devices[addr].readfrom_into(buf, stop)

    def writeto(self, addr, buf, stop=True):
        """
        Write the bytes from buf to the peripheral specified by addr.

        If a NACK is received following the write of a byte from buf then the remaining bytes are
        not sent. If stop is true then a STOP condition is generated at the end of the transfer,
        even if a NACK is received.

        The function returns the number of ACKs that were received.
        """
        if addr not in self.devices:
            raise OSError(errno.ENODEV)
        return self.devices[addr].writeto(buf, stop)

    # Memory operations
    def readfrom_mem(
        self, addr, memaddr, nbytes, *args, addrsize=8
    ):  # pylint: disable=unused-argument
        """
        Read nbytes from the peripheral specified by addr, starting at memaddr.

        Starting from the memory address specified by memaddr. The argument addrsize specifies the
        address size in bits.

        Returns a bytes object with the data read.
        """
        if addr not in self.devices:
            raise OSError(errno.ENODEV)
        return self.devices[addr].readfrom_mem(memaddr, nbytes)

    def readfrom_mem_into(self, addr, memaddr, buf, *args, addrsize=8):
        """
        Read into buf from the peripheral specified by addr, starting at memaddr.

        The number of bytes read is the length of buf. The argument addrsize specifies the address
        size in bits.

        The method returns None.
        """
        if addr not in self.devices:
            raise OSError(errno.ENODEV)
        return self.devices[addr].readfrom_mem_into(memaddr, buf)

    def writeto_mem(self, addr, memaddr, buf, *args, addrsize=8):
        """
        Write buf to the peripheral specified by addr, starting at memaddr.

        The number of bytes written is the length of buf. The argument addrsize specifies the
        address size in bits.

        The method returns None.
        """
        if addr not in self.devices:
            raise OSError(errno.ENODEV)
        self.devices[addr].writeto_mem(memaddr, buf)


class SPI:
    """
    Unittest support class for machine.SPI
    """

    def __init__(self, id=None):  # pylint: disable=unused-argument,redefined-builtin
        """
        Construct an SPI object on the given bus, id.
        """
        self.readbuf = b""

    # SPI Methods
    def init(
        self,
        baudrate=1000000,
        *,
        polarity=0,
        phase=0,
        bits=8,
        firstbit=None,
        sck=None,
        mosi=None,
        miso=None,
        pins=None,
    ):
        """
        Initialise the SPI bus with the given parameters
        """

    def deinit(self):
        """
        Turn off the SPI bus
        """

    def read(self, nbytes, write=0x00):  # pylint: disable=unused-argument
        """
        Read a number of bytes specified by nbytes.

        Continuously writes the single byte given by write, to ensure read data is clocked.

        Returns a bytes object with the data that was read.
        """
        return self.readbuf[:nbytes]

    def readinto(self, buf, write=0x00):
        """
        Read into the buffer specified by buf.

        Number of bytes read is the length of the buffer.
        Continuously writing the single byte given by write, to ensure read data is clocked.

        Returns None.
        """

    def write(self, buf):
        """
        Write the bytes contained in buf.

        Returns None.
        """

    def write_readinto(self, write_buf, read_buf):
        """
        Write the bytes from write_buf while reading into read_buf.

        The buffers can be the same or different, but both buffers must have the same length.

        Returns None.
        """


class Pin:
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
        self._irq_handler = None
        self._irq_trigger = None

    def init(self, mode=0, pull=0, alt=0):
        self._mode = mode
        self._pull = pull
        self._alt = alt

    def value(self, new_value=None):
        if new_value is not None:
            old_value = self._value
            self._value = int(new_value)

            if self._irq_trigger and self._irq_handler:
                if self._irq_trigger & self.IRQ_RISING and self._value > old_value:
                    micropython.schedule(self._irq_handler, self)
                if self._irq_trigger & self.IRQ_FALLING and self._value < old_value:
                    micropython.schedule(self._irq_handler, self)
            return None
        return self._value

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def irq(
        self, handler=None, trigger=IRQ_FALLING | IRQ_RISING, priority=1, wake=None, hard=False
    ):
        self._irq_handler = handler
        self._irq_trigger = trigger
        return self  # non-standard return value

    def mode(self):
        return self._mode

    def __call__(self, x=None):
        return self.value(x)


class ADC:
    """
    Unittest support class for machine.ADC.

    Modified from radiata/src/firmware/test/mocks.py
    """

    def __init__(self, pin):
        self.pin = pin
        self.value_u16 = 0

    # Methods
    def init(self, *, sample_ns, atten):
        """
        Apply the given settings to the ADC.

        Only those arguments that are specified will be changed.
        """

    def block(self):
        """
        Return the ADCBlock instance associated with this ADC object.
        """

    def read_u16(self):
        """
        Take an analog reading and return an integer in the range 0-65535.

        The return value represents the raw reading taken by the ADC.
        """
        return self.value_u16

    def read_uv(self):
        """
        Take an analog reading and return an integer value with units of microvolts.

        It is up to the particular port whether or not this value is calibrated, and how
        calibration is done.
        """

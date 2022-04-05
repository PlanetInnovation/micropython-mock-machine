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
tmp117 driver taken from radiata
"""

import struct

#from micropython import const


class TMP117:
    # Datasheet: https://www.ti.com/lit/ds/symlink/tmp117.pdf
    I2C_ADDR = 0x48  # Default address: ADD0 == Ground == 1001000
    REG_DEVICE_ID = 0x0F
    REG_TEMP_RESULT = 0x00
    TEMP_RESOLUTION = 0.0078125

    def __init__(self, i2c=None, addr=I2C_ADDR):
        if not i2c:
            raise ValueError("I2C object needed")
        self._i2c = i2c
        self._addr = addr
        self._check_device()

    def _check_device(self):
        """Check basic comms; REG_DEVICE_ID should always be 0x0117 """
        id_ = self._i2c.readfrom_mem(self._addr, TMP117.REG_DEVICE_ID, 2)
        unpacked = struct.unpack(">H", id_)  # ">H" == big endian, two bytes, unsigned
        if unpacked[0] != 0x0117:
            raise ValueError("Incorrect DEVICE ID (expect '0x117') or bad I2C comms")

    def get_temperature(self):
        t = self._i2c.readfrom_mem(self._addr, TMP117.REG_TEMP_RESULT, 2)
        unpacked = struct.unpack(">h", t)  # ">h" == big endian, two bytes, signed
        return unpacked[0] * TMP117.TEMP_RESOLUTION

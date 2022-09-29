# -*- coding: utf-8 -*-
#
# PI Background IP
# Copyright (c) 2021, Planet Innovation
# 436 Elgar Road, Box Hill, 3128, VIC, Australia
# Phone: +61 3 9945 7510
#
# The copyright to the computer program(s) herein is the property of
# Planet Innovation, Australia.
# The program(s) may be used and/or copied only with the written permission
# of Planet Innovation or in accordance with the terms and conditions
# stipulated in the agreement/contract under which the program(s) have been
# supplied.
#


class HardwareRevision:
    """Hardware Revision driver."""

    def __init__(self, pin_0, pin_1, spi, cs):
        """
        Parameters:
        pin_0 (Pin): pin corresponding to `HW0` on the device schematic
        pin_1 (Pin): pin corresponding to `HW1` on the device schematic
        spi (SPI): SPI bus connected to the SPI flash
        cs (Pin): pin connected to the SPI flash CS
        """
        self._pin_0 = pin_0
        self._pin_1 = pin_1
        self._spi = spi
        self._cs = cs

    def read(self):
        return 1 * self._pin_0.value() + 2 * self._pin_1.value()

    def read_spi_flash_size(self):
        """
        Return number of bytes in the external SPI flash.
        """
        self._cs(0)
        rdid = self._spi.read(4, 0x9F)
        self._cs(1)
        return 1 << rdid[3]

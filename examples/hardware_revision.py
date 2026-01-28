# -*- coding: utf-8 -*-
#
# Copyright (c) 2020-2025 Planet Innovation Pty Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


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

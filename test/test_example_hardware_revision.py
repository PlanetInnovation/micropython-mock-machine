# -*- coding: utf-8 -*-
#
# PI Background IP
# Copyright (c) 2022, Planet Innovation
# 436 Elgar Road, Box Hill, 3128, VIC, Australia
# Phone: +61 3 9945 7510
#
# The copyright to the computer program(s) herein is the property of
# Planet Innovation, Australia.
# The program(s) may be used and/or copied only with the written permission
# of Planet Innovation or in accordance with the terms and conditions
# stipulated in the agreement/contract under which the program(s) have been
# supplied.

import unittest

from examples.hardware_revision import HardwareRevision
from mock_machine import SPI, Pin


class TestHardwareRevision(unittest.TestCase):
    def setUp(self):
        self.pin_0 = Pin("D0", Pin.IN)
        self.pin_1 = Pin("D1", Pin.IN)
        self.spi = SPI()
        self.cs = Pin("SPI1_CS1")
        self.hardware_revision = HardwareRevision(self.pin_0, self.pin_1, self.spi, self.cs)

    def test_hardware_revision_returns_0(self):
        self.pin_0.value(0)
        self.pin_1.value(0)
        self.assertEqual(self.hardware_revision.read(), 0)

    def test_hardware_revision_returns_1(self):
        self.pin_0.value(1)
        self.pin_1.value(0)
        self.assertEqual(self.hardware_revision.read(), 1)

    def test_hardware_revision_returns_2(self):
        self.pin_0.value(0)
        self.pin_1.value(1)
        self.assertEqual(self.hardware_revision.read(), 2)

    def test_hardware_revision_returns_3(self):
        self.pin_0.value(1)
        self.pin_1.value(1)
        self.assertEqual(self.hardware_revision.read(), 3)

    def test_hardware_revision_reads_spi_size(self):
        self.spi.read_buf = b"\x9F\xC2\x23\x15"  # RDID for MX25V1635F
        self.assertEqual(self.hardware_revision.read_spi_flash_size(), 2 * 1024 * 1024)
        self.spi.read_buf = b"\x9F\xC2\x20\x19"  # RDID for MX25L25673G
        self.assertEqual(self.hardware_revision.read_spi_flash_size(), 32 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()

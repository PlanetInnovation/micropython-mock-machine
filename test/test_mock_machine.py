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

from mock_machine import I2C, I2CDevice


class TestI2C(unittest.TestCase):
    """Class for testing I2C class using I2CDevice."""

    SCAN_ADDR_MIN = 0x08
    SCAN_ADDR_MAX = 0x77
    ADDR_TEST_CASES = (SCAN_ADDR_MIN, SCAN_ADDR_MAX)

    NO_SCAN_TEST_CASES = (SCAN_ADDR_MIN - 1, SCAN_ADDR_MAX + 1)

    NO_DEVICE_ADDR = 0x09

    MEMADDR_TEST_CASES = (0x00, 0x05, 0x0A, 0x0F, 0x55, 0xAA, 0xFF)

    def setUp(self):
        # Make a mock I2C bus with mock I2C devices added to it
        self.i2c = I2C()
        self.devices = {}

        for addr in self.ADDR_TEST_CASES:
            # Make a I2C devices with LP55281 init and add to I2C bus
            self.devices[addr] = I2CDevice(addr, self.i2c)

    def test_scan(self):
        """Test scan of devices with valid addresses."""
        scan_list = self.i2c.scan()
        for addr in self.ADDR_TEST_CASES:
            with self.subTest(addr=addr):
                self.assertIn(addr, scan_list)

    def test_no_scan(self):
        """Test scan doesn't detect unexpected devices."""
        scan_list = self.i2c.scan()
        for addr in range(self.SCAN_ADDR_MIN + 1, self.SCAN_ADDR_MAX):
            with self.subTest(addr=addr):
                self.assertFalse(addr in scan_list)

    def test_scan_hidden(self):
        """Test scan doesn't detect devices outside of valid addresses."""
        for addr in self.NO_SCAN_TEST_CASES:
            # Add device only for this test
            I2CDevice(addr, self.i2c)

        scan_list = self.i2c.scan()
        for addr in self.NO_SCAN_TEST_CASES:
            with self.subTest(addr=addr):
                self.assertFalse(addr in scan_list)

    def test_no_device_error(self):
        """Test no device error correctly sent from applicable operators."""
        ADDR = self.NO_DEVICE_ADDR
        MEMADDR = 0x00
        NBYTES = 0
        buf = bytearray(0)

        with self.subTest(addr=ADDR, operator="readfrom"):
            with self.assertRaises(OSError):
                self.i2c.readfrom(ADDR, NBYTES)
        with self.subTest(addr=ADDR, operator="readfrom_into"):
            with self.assertRaises(OSError):
                self.i2c.readfrom_into(ADDR, buf)
        with self.subTest(addr=ADDR, operator="writeto"):
            with self.assertRaises(OSError):
                self.i2c.writeto(ADDR, buf)
        with self.subTest(addr=ADDR, operator="readfrom_mem"):
            with self.assertRaises(OSError):
                self.i2c.readfrom_mem(ADDR, MEMADDR, NBYTES)
        with self.subTest(addr=ADDR, operator="readfrom_mem_into"):
            with self.assertRaises(OSError):
                self.i2c.readfrom_mem_into(ADDR, MEMADDR, buf)
        with self.subTest(addr=ADDR, operator="writeto_mem"):
            with self.assertRaises(OSError):
                self.i2c.writeto_mem(ADDR, MEMADDR, buf)

    def test_read_unknown_memaddr(self):
        """Test unknown mem addr error correctly sent from applicable operators."""
        NBYTES = 0
        buf = bytearray(0)
        for addr in self.ADDR_TEST_CASES:
            for memaddr in self.MEMADDR_TEST_CASES:
                with self.subTest(addr=addr, memaddr=memaddr, operator="readfrom_mem"):
                    with self.assertRaises(IndexError):
                        self.i2c.readfrom_mem(addr, memaddr, NBYTES)
                with self.subTest(addr=addr, memaddr=memaddr, operator="readfrom_mem_into"):
                    with self.assertRaises(IndexError):
                        self.i2c.readfrom_mem_into(addr, memaddr, buf)

    def test_read_insufficient_none(self):
        """Test insufficient bytes error correctly sent from applicable operators."""
        NBYTES = 1
        buf = bytearray(1)
        for addr in self.ADDR_TEST_CASES:
            # Directly manipulate general readbuf with zero bytes
            self.devices[addr].readbuf = bytes(0)
            with self.subTest(addr=addr, operator="readfrom"):
                with self.assertRaises(ValueError):
                    self.i2c.readfrom(addr, NBYTES)
            with self.subTest(addr=addr, operator="readfrom_into"):
                with self.assertRaises(ValueError):
                    self.i2c.readfrom_into(addr, buf)
            for memaddr in self.MEMADDR_TEST_CASES:
                # Directly manipulate address memaddr with zero bytes
                self.devices[addr].register_values[memaddr] = bytes(0)
                with self.subTest(addr=addr, memaddr=memaddr, operator="readfrom_mem"):
                    with self.assertRaises(ValueError):
                        self.i2c.readfrom_mem(addr, memaddr, NBYTES)
                with self.subTest(addr=addr, memaddr=memaddr, operator="readfrom_mem_into"):
                    with self.assertRaises(ValueError):
                        self.i2c.readfrom_mem_into(addr, memaddr, buf)

    def test_read_insufficient_some(self):
        """Test insufficient bytes error correctly sent from applicable operators."""
        NBYTES = 3
        buf = bytearray(3)
        for addr in self.ADDR_TEST_CASES:
            # Directly manipulate general readbuf with too few bytes
            self.devices[addr].readbuf = b"AB"
            with self.subTest(addr=addr, operator="readfrom"):
                with self.assertRaises(ValueError):
                    self.i2c.readfrom(addr, NBYTES)
            with self.subTest(addr=addr, operator="readfrom_into"):
                with self.assertRaises(ValueError):
                    self.i2c.readfrom_into(addr, buf)
            for memaddr in self.MEMADDR_TEST_CASES:
                # Directly manipulate address memaddr with too few bytes
                self.devices[addr].register_values[memaddr] = b"AB"
                with self.subTest(addr=addr, memaddr=memaddr, operator="readfrom_mem"):
                    with self.assertRaises(ValueError):
                        self.i2c.readfrom_mem(addr, memaddr, NBYTES)
                with self.subTest(addr=addr, memaddr=memaddr, operator="readfrom_mem_into"):
                    with self.assertRaises(ValueError):
                        self.i2c.readfrom_mem_into(addr, memaddr, buf)

    def test_read(self):
        """Test valid reads from applicable operators."""
        NBYTES = 3
        buf = bytearray(3)
        for addr in self.ADDR_TEST_CASES:
            # Directly manipulate general readbuf with enough bytes
            self.devices[addr].readbuf = b"ABC"
            with self.subTest(addr=addr, operator="readfrom"):
                out = self.i2c.readfrom(addr, NBYTES)
                self.assertEqual(out, b"ABC")
            with self.subTest(addr=addr, operator="readfrom_into"):
                self.i2c.readfrom_into(addr, buf)
                self.assertEqual(buf, b"ABC")
            for memaddr in self.MEMADDR_TEST_CASES:
                # Directly manipulate address memaddr with enough bytes
                self.devices[addr].register_values[memaddr] = b"ABC"
                with self.subTest(addr=addr, memaddr=memaddr, operator="readfrom_mem"):
                    out = self.i2c.readfrom_mem(addr, memaddr, NBYTES)
                    self.assertEqual(out, b"ABC")
                with self.subTest(addr=addr, memaddr=memaddr, operator="readfrom_mem_into"):
                    self.i2c.readfrom_mem_into(addr, memaddr, buf)
                    self.assertEqual(buf, b"ABC")

    def test_writeto(self):
        """Test basic writeto()."""
        buf = "ABC"
        for addr in self.ADDR_TEST_CASES:
            with self.subTest(addr=addr):
                num = self.i2c.writeto(addr, buf)
                self.assertEqual(num, len(buf))

    def test_writeto_mem(self):
        """Test basic write_to_mem()."""
        buf = "ABC"
        for addr in self.ADDR_TEST_CASES:
            for memaddr in self.MEMADDR_TEST_CASES:
                with self.subTest(addr=addr, memaddr=memaddr):
                    self.i2c.writeto_mem(addr, memaddr, buf)
                    # Directly check internal memaddr value
                    self.assertEqual(self.devices[addr].register_values[memaddr], buf)


if __name__ == "__main__":
    unittest.main()

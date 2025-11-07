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

import time
import unittest

from mock_machine import I2C, I2CDevice, Pin, UART


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


class TestPin(unittest.TestCase):
    @staticmethod
    def test_pin_irq():
        fired = False

        def cb(_):
            nonlocal fired
            fired = True

        pin = Pin("one")
        pin.value(0)
        pin.irq(cb, trigger=Pin.IRQ_RISING)

        assert not fired

        pin.value(1)

        time.sleep_ms(1)  # pylint: disable=no-member

        assert fired

    @staticmethod
    def test_pin_reused():

        pin_first_user = Pin("one")
        pin_different = Pin("two")
        pin_second_user = Pin("one")

        pin_first_user.value(1)
        pin_different.value(0)

        assert pin_first_user.value() == 1
        assert pin_different.value() == 0, "Should not have changed"
        assert pin_second_user.value() == 1

        pin_second_user.value(0)

        assert pin_first_user.value() == 0
        assert pin_different.value() == 0, "Should not have changed"
        assert pin_second_user.value() == 0


class TestUART(unittest.TestCase):
    """Test UART class with RingIO buffers."""

    def test_basic_read_write(self):
        """Test basic read and write operations."""
        uart = UART()

        # Write data
        written = uart.write(b"Hello")
        self.assertEqual(written, 5)

        # Read back written data
        data = uart.get_written_data()
        self.assertEqual(data, b"Hello")

    def test_initial_data(self):
        """Test UART with initial data_for_read."""
        uart = UART(data_for_read=b"Initial data")

        # Should be able to read initial data
        data = uart.read()
        self.assertEqual(data, b"Initial data")

    def test_inject_data(self):
        """Test dynamic data injection."""
        uart = UART()

        # Initially no data
        self.assertEqual(uart.any(), 0)

        # Inject some data
        injected = uart.inject_data(b"Injected")
        self.assertEqual(injected, 8)
        self.assertEqual(uart.any(), 8)

        # Read it back
        data = uart.read()
        self.assertEqual(data, b"Injected")
        self.assertEqual(uart.any(), 0)

    def test_multiple_injections(self):
        """Test multiple data injections."""
        uart = UART()

        uart.inject_data(b"First ")
        uart.inject_data(b"Second ")
        uart.inject_data(b"Third")

        # All data should be concatenated in buffer
        self.assertEqual(uart.any(), 18)
        data = uart.read()
        self.assertEqual(data, b"First Second Third")

    def test_partial_read(self):
        """Test reading partial data."""
        uart = UART(data_for_read=b"Hello World")

        # Read first 5 bytes
        data = uart.read(5)
        self.assertEqual(data, b"Hello")
        self.assertEqual(uart.any(), 6)

        # Read remaining
        data = uart.read()
        self.assertEqual(data, b" World")
        self.assertEqual(uart.any(), 0)

    def test_readinto(self):
        """Test readinto buffer operation."""
        uart = UART(data_for_read=b"Test data")

        buf = bytearray(4)
        n = uart.readinto(buf)

        self.assertEqual(n, 4)
        self.assertEqual(buf, b"Test")
        self.assertEqual(uart.any(), 5)

    def test_readline(self):
        """Test readline operation."""
        uart = UART(data_for_read=b"Line1\nLine2\nLine3")

        line1 = uart.readline()
        self.assertEqual(line1, b"Line1\n")

        line2 = uart.readline()
        self.assertEqual(line2, b"Line2\n")

        line3 = uart.readline()
        self.assertEqual(line3, b"Line3")

    def test_any(self):
        """Test any() returns correct byte count."""
        uart = UART()

        self.assertEqual(uart.any(), 0)

        uart.inject_data(b"12345")
        self.assertEqual(uart.any(), 5)

        uart.read(2)
        self.assertEqual(uart.any(), 3)

        uart.read()
        self.assertEqual(uart.any(), 0)

    def test_buffer_overflow(self):
        """Test behavior when buffer is full."""
        # Create small buffer
        uart = UART(rxbuf=8)

        # Fill buffer (8 bytes max, RingIO reserves 1)
        written = uart.inject_data(b"12345678")
        self.assertTrue(written <= 8)

        # Try to inject more - should write less than requested
        overflow = uart.inject_data(b"90")
        self.assertTrue(overflow < 2)

    def test_write_buffer_capture(self):
        """Test that written data is captured correctly."""
        uart = UART()

        uart.write(b"AT+")
        uart.write(b"CMD")
        uart.write(b"\r\n")

        # Should capture all writes
        written_data = uart.get_written_data()
        self.assertEqual(written_data, b"AT+CMD\r\n")

    def test_ioctl_poll(self):
        """Test ioctl MP_STREAM_POLL operation."""
        uart = UART()

        # No data - should return 0
        result = uart.ioctl(3, 0)  # MP_STREAM_POLL
        self.assertEqual(result, 0)

        # With data - should return MP_STREAM_POLL_RD
        uart.inject_data(b"data")
        result = uart.ioctl(3, 0)
        self.assertEqual(result, 0x0001)  # MP_STREAM_POLL_RD

    def test_custom_buffer_sizes(self):
        """Test UART with custom buffer sizes."""
        uart = UART(rxbuf=16, txbuf=32)

        # Should be able to inject up to rxbuf size
        data = b"x" * 15
        written = uart.inject_data(data)
        self.assertTrue(written >= 10)  # At least most of it should fit

    def test_backward_compatibility(self):
        """Test backward compatibility with read_buf_len parameter."""
        uart = UART(read_buf_len=64, data_for_read=b"Test")

        data = uart.read()
        self.assertEqual(data, b"Test")

    def test_empty_operations(self):
        """Test operations on empty buffers."""
        uart = UART()

        # Reading from empty buffer
        data = uart.read()
        self.assertEqual(data, b"")

        data = uart.read(10)
        self.assertEqual(data, b"")

        line = uart.readline()
        self.assertEqual(line, b"")

        buf = bytearray(4)
        n = uart.readinto(buf)
        self.assertEqual(n, 0)

    def test_constructor_params(self):
        """Test UART accepts standard constructor parameters."""
        # Should accept all standard UART parameters without error
        uart = UART(
            id=1,
            baudrate=115200,
            bits=8,
            parity=None,
            stop=1,
            tx="P1",
            rx="P2",
            txbuf=512,
            rxbuf=512,
            timeout=1000,
            timeout_char=10,
            invert=0,
            flow=0,
        )

        # Basic functionality should still work
        uart.inject_data(b"Test")
        data = uart.read()
        self.assertEqual(data, b"Test")


if __name__ == "__main__":
    unittest.main()

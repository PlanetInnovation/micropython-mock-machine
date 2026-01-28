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

    def test_pin_board_magic_mode_default(self):
        """Test Pin.board and Pin.cpu default to magic mode without configuration"""
        # Should return any pin name in magic mode (default)
        assert Pin.board.LED_GREEN == "LED_GREEN"
        assert Pin.board.ANY_PIN_NAME == "ANY_PIN_NAME"
        assert Pin.board.SPI5_SCK == "SPI5_SCK"

        # Pin.cpu should also work in magic mode
        assert Pin.cpu.LED_GREEN == "LED_GREEN"
        assert Pin.cpu.ANY_PIN_NAME == "ANY_PIN_NAME"

    def test_pin_board_magic_mode_explicit(self):
        """Test Pin.board with explicit None configuration stays in magic mode"""
        Pin.board.configure(None)
        assert Pin.board.SOME_PIN == "SOME_PIN"
        assert Pin.board.ANOTHER_PIN == "ANOTHER_PIN"

    def test_pin_board_strict_mode_with_csv(self):
        """Test Pin.board in strict mode with a valid pins.csv file"""
        import os

        # Create a test pins.csv file
        test_path = "test_pins_strict.csv"
        try:
            with open(test_path, "w") as f:
                f.write("# Test pins file\n")
                f.write("LED_GREEN,GPIO_01\n")
                f.write("LED_RED,GPIO_02\n")
                f.write("SPI5_SCK,GPIO_10\n")
                f.write("-HIDDEN_PIN,GPIO_99\n")  # Should be skipped
                f.write("\n")  # Empty line
                f.write("# Another comment\n")

            # Configure with the test CSV
            Pin.board.configure(test_path)

            # Pin.board: board name → CPU pin
            assert Pin.board.LED_GREEN == "GPIO_01"
            assert Pin.board.LED_RED == "GPIO_02"
            assert Pin.board.SPI5_SCK == "GPIO_10"

            # Pin.cpu: CPU pin → CPU pin (identity)
            assert Pin.cpu.GPIO_01 == "GPIO_01"
            assert Pin.cpu.GPIO_02 == "GPIO_02"
            assert Pin.cpu.GPIO_10 == "GPIO_10"

            # Hidden pin should not be accessible by board name
            with self.assertRaises(AttributeError) as ctx:
                _ = Pin.board.HIDDEN_PIN
            assert "not defined in pins.csv" in str(ctx.exception)

            # Hidden pin's CPU pin (GPIO_99) should not be in Pin.cpu either
            with self.assertRaises(AttributeError) as ctx:
                _ = Pin.cpu.GPIO_99
            assert "not defined in pins.csv" in str(ctx.exception)

            # Undefined pin should raise error in strict mode
            with self.assertRaises(AttributeError) as ctx:
                _ = Pin.board.UNDEFINED_PIN
            assert "not defined in pins.csv" in str(ctx.exception)

            with self.assertRaises(AttributeError) as ctx:
                _ = Pin.cpu.UNDEFINED_PIN
            assert "not defined in pins.csv" in str(ctx.exception)

        finally:
            # Clean up test file
            try:
                os.remove(test_path)
            except OSError:
                pass

    def test_pin_board_fallback_on_missing_file(self):
        """Test Pin.board falls back to magic mode if CSV file doesn't exist"""
        # Configure with non-existent file
        Pin.board.configure("/this/path/does/not/exist/pins.csv")

        # Should fall back to magic mode
        assert Pin.board.ANY_PIN == "ANY_PIN"
        assert Pin.board.ANOTHER_PIN == "ANOTHER_PIN"

    def test_pin_board_reconfigure(self):
        """Test Pin.board can be reconfigured"""
        import os

        # Create test CSV files
        test_path1 = "test_pins_a.csv"
        test_path2 = "test_pins_b.csv"

        try:
            # First configuration
            with open(test_path1, "w") as f:
                f.write("PIN_A,GPIO_01\n")

            # Second configuration
            with open(test_path2, "w") as f:
                f.write("PIN_B,GPIO_02\n")

            # Configure with first CSV
            Pin.board.configure(test_path1)
            assert Pin.board.PIN_A == "GPIO_01"  # Pin.board returns CPU pin
            with self.assertRaises(AttributeError):
                _ = Pin.board.PIN_B

            # Reconfigure with second CSV
            Pin.board.configure(test_path2)
            assert Pin.board.PIN_B == "GPIO_02"  # Pin.board returns CPU pin
            with self.assertRaises(AttributeError):
                _ = Pin.board.PIN_A

            # Reconfigure back to magic mode
            Pin.board.configure(None)
            assert Pin.board.PIN_A == "PIN_A"  # Magic mode returns name as-is
            assert Pin.board.PIN_B == "PIN_B"

        finally:
            # Clean up test files
            try:
                os.remove(test_path1)
            except OSError:
                pass
            try:
                os.remove(test_path2)
            except OSError:
                pass


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

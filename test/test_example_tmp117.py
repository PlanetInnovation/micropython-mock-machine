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
Test case taken from radiata used to test the tmp117 driver
"""

import unittest
from collections import namedtuple

from examples.tmp117 import TMP117
from mock_machine import I2C, I2CDevice

TestCase = namedtuple("TestCase", ["temperature", "bytes"])

TEST_CASES = [
    TestCase(-256, bytes([0x80, 0x00])),
    TestCase(-25, bytes([0xF3, 0x80])),
    TestCase(-0.1250, bytes([0xFF, 0xF0])),
    TestCase(-0.0078125, bytes([0xFF, 0xFF])),
    TestCase(0, bytes([0x00, 0x00])),
    TestCase(0.0078125, bytes([0x00, 0x01])),
    TestCase(0.1250, bytes([0x00, 0x10])),
    TestCase(1, bytes([0x00, 0x80])),
    TestCase(25, bytes([0x0C, 0x80])),
    TestCase(100, bytes([0x32, 0x00])),
    TestCase(255.9921, bytes([0x7F, 0xFF])),
]


class TestImagingModuleADC(unittest.TestCase):
    def setUp(self):
        # Make a mock I2C bus with mock I2C device added to it
        self.i2c = I2C()
        self.device = I2CDevice(TMP117.I2C_ADDR, self.i2c)

    def test_bad_device_id_register_fails_to_init(self):
        with self.assertRaises(IndexError):
            TMP117(self.i2c)

    def test_tmp117_initialises_with_valid_device_id_register(self):
        self.device.register_values[TMP117.REG_DEVICE_ID] = bytes([0x01, 0x17])
        TMP117(self.i2c)

    def test_datasheet_examples(self):
        self.device.register_values[TMP117.REG_DEVICE_ID] = bytes([0x01, 0x17])
        tmp117 = TMP117(self.i2c)

        for test_case in TEST_CASES:
            with self.subTest(test_case=test_case):
                self.device.register_values[TMP117.REG_TEMP_RESULT] = test_case.bytes
                self.assertAlmostEqual(tmp117.get_temperature(), test_case.temperature, places=2)


def run():
    unittest.main()

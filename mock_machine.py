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
"""

import errno
import io
import logging
import time

try:
    from typing import Dict, Optional
except ImportError:
    pass

import asyncio
import micropython
from micropython import const

log = logging.getLogger("mock_machine")

# Not concerned about unused arguments in mocks
# pylint: disable=unused-argument
# pylint: disable=no-member


def register_as_machine():
    """
    This will register mock_machine as machine so it can be imported by other
    modules expecting `import machine` to work.
    """
    import sys

    log.warning("All imports of machine are mocked from here on")
    sys.modules["machine"] = sys.modules["mock_machine"]


# machine module interfaces

SOFT_RESET = 0
PWRON_RESET = 1
HARD_RESET = 2
WDT_RESET = 3
DEEPSLEEP_RESET = 4
__reset_cause__ = PWRON_RESET


def reset_cause():
    """
    https://docs.micropython.org/en/latest/library/machine.html#machine.reset_cause
    """
    return __reset_cause__


class ADC:
    pin_adc_map: Dict[Pin, int] = {}  # noqa: F821
    """
    Unittest support class for machine.ADC.

    https://docs.micropython.org/en/latest/library/machine.ADC.html
    """

    def __init__(self, pin):
        self.pin = pin

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
        if self.pin in ADC.pin_adc_map:
            return ADC.pin_adc_map[self.pin]

        return 0

    def read_uv(self):
        """
        Take an analog reading and return an integer value with units of microvolts.

        It is up to the particular port whether or not this value is calibrated, and how
        calibration is done.
        Note: stm32 port does not include this functionality as of August 2023.
        """
        return self.value_uv


class I2C:
    """
    Unittest support class for machine.I2C.

    https://docs.micropython.org/en/latest/library/machine.I2C.html
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


class I2CDevice:
    """
    A single I2C device added to a mock_machine.I2C bus.

    This is a utility class for simulating a real device, not
    representative of a "real" micropython machine class.
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


class RegisterBasedI2CDevice(I2CDevice):
    """
    I2C device that uses register-based protocol (common for RTCs, sensors, etc.).

    This device simulates the common I2C protocol where:
    1. Master writes register address
    2. Master reads/writes data from/to that register

    This matches the protocol used by many I2C devices like the PCF85063 RTC.
    """

    def __init__(self, addr, i2c, register_count=32):
        """
        Initialize register-based I2C device.

        Args:
            addr: I2C address of the device
            i2c: I2C bus to attach to
            register_count: Number of registers (default 32)
        """
        super().__init__(addr, i2c)
        self.registers = bytearray(register_count)
        self.current_register = None

    def writeto(self, buf, stop=True):
        """
        Write bytes to device.

        First byte is register address, subsequent bytes are written to registers.
        """
        if len(buf) == 0:
            return 0

        # First byte is register address
        self.current_register = buf[0]

        # If more bytes, write them to registers
        if len(buf) > 1:
            for i, value in enumerate(buf[1:]):
                reg_addr = self.current_register + i
                if reg_addr < len(self.registers):
                    self.registers[reg_addr] = value

        return len(buf)

    def readfrom_into(self, buf, stop=True):
        """
        Read bytes from device into buffer.

        Reads from the current register address set by previous writeto.
        """
        if self.current_register is None:
            raise ValueError("No register address set")

        for i in range(len(buf)):
            reg_addr = self.current_register + i
            if reg_addr < len(self.registers):
                buf[i] = self.registers[reg_addr]
            else:
                buf[i] = 0


class Memory:
    """
    https://docs.micropython.org/en/latest/library/machine.html#memory-access
    """

    def __init__(self, data):
        self.data = data

    def __getitem__(self, idx):
        return self.data


mem8 = Memory(0xFF)
mem16 = Memory(0xFFFF)
mem32 = Memory(0xFFFFFFFF)


class Pin:
    """
    Unittest support class for machine.Pin

    Allows manual setting of input or output pin's value.

    https://docs.micropython.org/en/latest/library/machine.Pin.html

    """

    # mode
    IN = 0
    OUT = 1
    OPEN_DRAIN = 2
    ALT = 3
    ALT_OPEN_DRAIN = 4
    ANALOG = 5

    # pull
    PULL_UP = 0
    PULL_DOWN = 1

    IRQ_RISING = 269549568
    IRQ_FALLING = 270598144

    pins: Dict[str, "Pin"] = {}

    """
    Configuring Pin.board and Pin.cpu definitions.
    The actual pin names for your project can be configured
    in this mock Pin class by providing your real board pins.csv file like:
    `Pin.board.configure("../path/to/my-board/pins.csv")`
    After this your mock Pin.board.<PIN_NAME> and Pin.cpu.<GPIO_NAME>
    attributes will work similar to the real hardware.
    """

    class _PinNamespace:
        """Base class for pin name namespaces (board/cpu)"""

        def __init__(self, column_index: int, namespace_name: str):
            self._pins: Dict[str, str] = {}
            self._magic_mode: bool = True
            self._column_index = column_index
            self._namespace_name = namespace_name

        def _load_pins(self, pins_csv_path: Optional[str] = None) -> None:
            """Load pins from CSV file

            Args:
                pins_csv_path: Explicit path to pins.csv file
                              - If provided and exists: STRICT mode (only defined pins allowed)
                              - If None or file missing: MAGIC mode (any pin name works)

            The pins.csv format expected is:
                BOARD_PIN,CPU_PIN
                # Comments start with #
                -HIDDEN_PIN,GPIO_yyy  # Pins starting with - are skipped
            """
            self._pins = {}

            if pins_csv_path is None:
                # No CSV specified - use magic mode for maximum compatibility
                self._magic_mode = True
                return

            try:
                with open(pins_csv_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if not line or line.startswith("#"):
                            continue

                        # Parse CSV: BOARD_PIN,CPU_PIN
                        parts = line.split(",")
                        if len(parts) >= 2:
                            board_pin = parts[0].strip()
                            cpu_pin = parts[1].strip()
                            # Skip hidden pins (prefixed with -)
                            if not board_pin.startswith("-"):
                                # Store mapping based on namespace type
                                if self._column_index == 0:
                                    # Pin.board: board name → CPU pin
                                    self._pins[board_pin] = cpu_pin
                                else:
                                    # Pin.cpu: CPU pin → CPU pin
                                    self._pins[cpu_pin] = cpu_pin

                # CSV loaded successfully - use strict mode
                self._magic_mode = False
                log.info(
                    f"Pin.{self._namespace_name} configured with "
                    f"{len(self._pins)} pins from {pins_csv_path}"
                )

            except OSError as e:
                # CSV file not found - fall back to magic mode
                self._magic_mode = True
                log.warning(
                    f"Pin.{self._namespace_name}: Could not load "
                    f"{pins_csv_path}, using magic mode: {e}"
                )

        def __getattr__(self, name: str) -> str:
            """Get a pin name from this namespace

            In strict mode (CSV loaded), only returns defined pins.
            In magic mode (no CSV), returns any requested name.
            """
            if name.startswith("_"):
                # Don't intercept private attributes
                raise AttributeError(f"Pin.{self._namespace_name} has no attribute '{name}'")
            if name in self._pins:
                return self._pins[name]
            if self._magic_mode:
                return name  # Return any requested name
            raise AttributeError(f"Pin.{self._namespace_name}.{name} not defined in pins.csv")

    class _PinBoard(_PinNamespace):
        """Board pin names namespace

        Maps board pin names to CPU pin names.
        Example: Pin.board.SPI5_SCK_NEN returns 'GPIO_AD_08'
        """

        def __init__(self):
            super().__init__(column_index=0, namespace_name="board")

        def configure(self, pins_csv_path: Optional[str] = None) -> None:
            """Configure Pin.board and Pin.cpu with pins from CSV file"""
            self._load_pins(pins_csv_path)
            # Also configure cpu namespace
            Pin.cpu._load_pins(pins_csv_path)  # noqa: F821

    class _PinCPU(_PinNamespace):
        """CPU pin names namespace

        Maps CPU pin names to themselves (identity mapping).
        Example: Pin.cpu.GPIO_AD_08 returns 'GPIO_AD_08'
        """

        def __init__(self):
            super().__init__(column_index=1, namespace_name="cpu")

    board = _PinBoard()
    cpu = _PinCPU()

    # pylint: disable=redefined-builtin
    def __new__(cls, id, mode=0, pull=0, value=None, drive=0, alt=-1):
        """
        If the matching pin is already created, keep that. It's config
        will be updated in __init__() below
        """
        if id in Pin.pins:
            return Pin.pins[id]
        self = super().__new__(cls)
        Pin.pins[id] = self
        return self

    # pylint: disable=redefined-builtin
    def __init__(self, id, mode=0, pull=0, value=None, drive=0, alt=-1):
        self._value = value
        self._mode = mode
        self._pull = pull
        self._alt = None
        self._irq_handler = None
        self._irq_trigger = None

    def init(self, mode=0, pull=0, alt=0, value=None):
        self._mode = mode
        self._pull = pull
        self._alt = alt
        self._value = value

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

    def high(self):
        self.value(1)

    def low(self):
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


class PWM:
    """
    https://docs.micropython.org/en/latest/library/machine.PWM.html
    """

    def __init__(
        self,
        dest: Pin,
        *,
        freq: int,
        duty_u16: Optional[int] = None,
        duty_ns: Optional[int] = None,
        invert: bool = False,
    ):
        self._pin = dest
        self._freq = freq
        self._duty_u16 = duty_u16
        self._duty_ns = duty_ns
        if duty_ns is None and duty_u16 is None:
            raise ValueError("Needs duty_ns or duty_u16 provided")
        self.invert = invert

    def init(self, freq, duty_u16, duty_ns):
        self._freq = freq
        self._duty_u16 = duty_u16
        self._duty_ns = duty_ns

    def deinit(self):
        self._freq = None
        self._duty_u16 = None
        self._duty_ns = None

    def freq(self, value=None):
        if value is None:
            return self._freq
        self._freq = value

    def duty_u16(self, value=None):
        if value is None:
            return self._duty_u16
        self._duty_u16 = value

    def duty_ns(self, value=None):
        if value is None:
            return self._duty_ns
        self._duty_ns = value


class RTC:
    """
    https://docs.micropython.org/en/latest/library/machine.RTC.html
    """

    def __init__(self):
        self._callback = None
        self._timeout = None
        self._stop = False
        self._running = False
        self._task = None  # don't start task yet

    def wakeup(self, timeout=None, callback=None):
        """
        Register a wakeup timer.

        :param timeout: Wakeup interval in ms
        :param callback: Function to call on wakeup
        """
        log.info("RTC: Registering a wakeup in: %s, callback is: %s", timeout, callback)

        self._timeout = timeout
        self._callback = callback
        if callback:
            assert callable(self._callback)

        # Start the async loop only when first used
        if not self._task:
            self._task = asyncio.create_task(self._wakeup())

    async def _wakeup(self):
        log.info("RTC: Starting RTC task")
        self._running = True

        while not self._stop:
            timeout = self._timeout if self._timeout else 1000  # default 1s
            await asyncio.sleep_ms(timeout)

            if self._callback:
                try:
                    self._callback()
                except Exception as e:
                    log.error("RTC callback raised: %s", e)

        self._running = False
        log.info("RTC: stopped wakeup task")

    def stop(self):
        log.info("RTC: Calling Stop")
        self._stop = True
        if self._task:
            while self._running:
                pass
            self._task = None

    @staticmethod
    def info():
        return 1 << 28  # Default "RTC is good" value

    @staticmethod
    def init():
        pass

    @staticmethod
    def datetime(datetime=None):
        now = time.time()
        t = tuple(time.localtime(now))
        return t[:3] + (t[6],) + t[3:6] + (round(now * 1000000) % 1000000,)


class Signal:
    """
    https://docs.micropython.org/en/latest/library/machine.Signal.html
    """

    def __init__(self, pin, invert):
        self.pin = pin
        self.invert = invert

    def on(self):
        self.pin.value(0 if self.invert else 1)

    def off(self):
        self.pin.value(1 if self.invert else 0)

    def value(self, val):
        self.pin.value(val)
        return self.pin.value()


class SPI:
    """
    Unittest support class for machine.SPI

    https://docs.micropython.org/en/latest/library/machine.SPI.html
    """

    def __init__(self, id=None):  # pylint: disable=unused-argument,redefined-builtin
        """
        Construct an SPI object on the given bus, id.
        """
        # Use write_buf/read_buf if dealing with the same data regardless of the
        # number of calls.
        self.write_buf = bytearray()  # what has been written last
        self.read_buf = bytearray()  # what to return from read

        # Use writes/reads if dealing with different data in different calls.
        self.writes = []  # what has been written in order of calls
        self.reads = []  # what to return from read in order of calls
        self.num_reads = 0  # the number of reads so far

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
        # Return the data from read_buf again and again, if specified.
        if self.read_buf:
            return self.read_buf[:nbytes]

        # Otherwise, return the data from reads in order of calls, if specified.
        if self.reads:
            index = self.num_reads
            self.num_reads += 1
            return self.reads[index]

        raise NotImplementedError

    def readinto(self, buf, write=0x00):
        """
        Read into the buffer specified by buf.

        Number of bytes read is the length of the buffer.
        Continuously writing the single byte given by write, to ensure read data is clocked.

        Returns None.
        """
        buf[:] = self.read(len(buf))

    def write(self, buf):
        """
        Write the bytes contained in buf.

        Returns None.
        """
        # Always record copy of the last written data to write_buf.
        self.write_buf = bytes(buf)

        # Always append copy of the written data to writes in order of calls.
        self.writes.append(bytes(buf))

    def write_readinto(self, write_buf, read_buf):
        """
        Write the bytes from write_buf while reading into read_buf.

        The buffers can be the same or different, but both buffers must have the same length.

        Returns None.
        """
        self.readinto(read_buf)
        self.write_buf = write_buf

    def reset(self):
        """
        Reset to the initial state of the mock.
        """
        self.writes = []
        self.reads = []
        self.num_reads = 0


class Timer:
    """
    https://docs.micropython.org/en/latest/library/machine.Timer.html
    """

    ONE_SHOT = 0
    PERIODIC = 1

    def __init__(self, id=0, channel=None, mode=None, period=None, callback=None):
        self._id = id  # Micropython timer first positional param is id.
        self._start = None
        self._period = period
        self._mode = mode
        self._callback = callback
        self._task = None
        self._channel = channel
        self._freq = 1000  # default frequency

        if mode or period or callback:
            self.init(freq=self._freq, mode=mode, period=period, callback=callback)

    def init(self, freq=1000, mode=PERIODIC, period=-1, callback=None):
        if self._task:
            self._task.cancel()
        self._freq = freq or 1000
        self._mode = mode
        self._period = period if period > 0 else 1000  # fallback to 1s
        self._callback = callback
        self._task = asyncio.create_task(self._timer())

    async def _timer(self):
        while True:
            await asyncio.sleep_ms(self._period)
            if self._callback:
                self._callback(time.time())
            if self._mode == self.PERIODIC:
                continue
            return

    def deinit(self):
        if self._task:
            self._task.cancel()
            self._task = None


class WDT:
    """
    https://docs.micropython.org/en/latest/library/machine.WDT.html
    """

    def __init__(self, timeout):
        self._timeout = timeout
        self._last_pat = time.ticks_ms()
        self._disabled = False
        self.running = True
        self._task = asyncio.create_task(self._tick())

    def disable(self):
        self._disabled = True
        self.running = False

    def feed(self):
        assert self._disabled or self.running, "you are late, WDT already stopped"
        self._last_pat = time.ticks_ms()

    async def _tick(self):
        log.info("Starting WDT loop, timeout is: %s", self._timeout)

        while self.running:
            await asyncio.sleep_ms(10)
            diff = time.ticks_ms() - self._last_pat

            if diff >= self._timeout:
                log.error("\nWDT timeout:%s > %s\n", diff, self._timeout)
                self.running = False
                raise RuntimeError()


class UART(io.IOBase):
    """
    Mock UART
    https://docs.micropython.org/en/latest/library/machine.UART.html
    """

    def __init__(
        self,
        id=None,
        baudrate=9600,
        bits=8,
        parity=None,
        stop=1,
        tx=None,
        rx=None,
        txbuf=256,
        rxbuf=256,
        timeout=0,
        timeout_char=0,
        invert=0,
        flow=0,
        read_buf_len=256,
        data_for_read=b"",
    ):
        rx_size = rxbuf if rxbuf != 256 else read_buf_len
        tx_size = txbuf

        # Create RingIO buffers for RX and TX
        self._rx_ring = micropython.RingIO(rx_size)
        self._tx_ring = micropython.RingIO(tx_size)

        if data_for_read:
            self.inject_data(data_for_read)

        super().__init__()

    def inject_data(self, data):
        """Inject data into read buffer to simulate receiving data."""
        return self._rx_ring.write(data)

    def write(self, data):
        return self._tx_ring.write(data)

    def read(self, nbytes=-1):
        if nbytes == -1:
            return self._rx_ring.read()
        return self._rx_ring.read(nbytes)

    def readinto(self, buf, nbytes=None):
        if nbytes is None:
            nbytes = len(buf)
        return self._rx_ring.readinto(buf, nbytes)

    def readline(self):
        return self._rx_ring.readline()

    def flush(self):
        pass

    def close(self):
        pass

    def any(self):
        return self._rx_ring.any()

    def ioctl(self, op, arg):
        # From micropython/py/stream.h
        # This allows the class to be used in asyncio.StreamReader etc.
        _MP_STREAM_POLL = const(3)
        _MP_STREAM_POLL_RD = const(0x0001)
        _MP_STREAM_FLUSH = const(1)
        _MP_STREAM_CLOSE = const(4)

        if op == _MP_STREAM_POLL:
            ret = _MP_STREAM_POLL_RD if self.any() else 0
            return ret
        elif op == _MP_STREAM_FLUSH:
            return self.flush()
        elif op == _MP_STREAM_CLOSE:
            return self.close()

        # Return -1 for unsupported ioctl operations
        return -1

    def get_written_data(self):
        """Get all data written to UART (for test assertions)."""
        return self._tx_ring.read()

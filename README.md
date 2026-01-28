# micropython-mock-machine

A MicroPython library that provides mock implementations of the `machine` module for unit testing.

This library allows you to test MicroPython drivers and applications that use the `machine` module without requiring actual hardware. Mock implementations are provided for common peripherals like I2C, SPI, Pin, ADC, and more.

## Features

Currently `mock_machine` implements:

- **I2C** - Inter-Integrated Circuit bus with device simulation
  - `init`, `deinit`, `scan`
  - `readfrom`, `readfrom_into`, `writeto`
  - `readfrom_mem`, `readfrom_mem_into`, `writeto_mem`
  - `add_device` (for simulating multiple devices on the bus)

- **SPI** - Serial Peripheral Interface
  - `init`, `deinit`
  - `read`, `readinto`, `write`, `write_readinto`

- **Pin** - Digital I/O pins
  - `init`, `value`, `on`, `off`, `high`, `low`
  - `irq` with IRQ_RISING and IRQ_FALLING triggers
  - `mode` configuration
  - `Pin.board` and `Pin.cpu` namespaces for pin name resolution

- **ADC** - Analog to Digital Converter
  - `read_u16`

- **PWM** - Pulse Width Modulation
  - Frequency and duty cycle control

- **UART** - Universal Asynchronous Receiver/Transmitter
  - Read/write operations with buffering

- **Timer** - Hardware timers
  - Periodic and one-shot modes

- **WDT** - Watchdog Timer
  - Timeout and feed operations

- **RTC** - Real Time Clock
  - Wakeup alarms and datetime

Additional utilities:
- **I2CDevice** - Helper class for simulating I2C devices with register-based interfaces
- **RegisterBasedI2CDevice** - Extended I2CDevice for testing register-based I2C devices (RTCs, sensors)
- **Signal** - Digital signal with inversion support

## Installation

### Using mip (recommended)

```python
import mip
mip.install("github:planetinnovation/micropython-mock-machine")
```

### Manual installation

Copy `mock_machine.py` to your MicroPython device's `/lib` directory.

## Usage

### Basic Example

```python
# In your test file
import mock_machine

# Register mock_machine as the machine module
mock_machine.register_as_machine()

# Now any import of 'machine' will use the mock
import machine

# Create mock hardware
i2c = machine.I2C(0)
pin = machine.Pin(0, machine.Pin.OUT)

# Use as normal
pin.value(1)
assert pin.value() == 1
```

### Simulating I2C Devices

```python
import mock_machine
from mock_machine import I2C, I2CDevice

# Create I2C bus
i2c = I2C(0)

# Create a mock device at address 0x68
device = I2CDevice(addr=0x68, i2c=i2c)

# Set up register values
device.register_values[0x00] = b'\x12\x34'  # WHO_AM_I register
device.register_values[0x01] = b'\x00\x00'  # Control register

# Your driver can now read from the device
data = i2c.readfrom_mem(0x68, 0x00, 2)
assert data == b'\x12\x34'
```

### Pin Interrupts

```python
import mock_machine
import asyncio

mock_machine.register_as_machine()
import machine

# Create a pin with interrupt
pin = machine.Pin(0, machine.Pin.IN)

# Set up interrupt handler
def pin_handler(pin):
    print(f"Pin interrupt! Value: {pin.value()}")

pin.irq(handler=pin_handler, trigger=machine.Pin.IRQ_RISING)

# Simulate pin change
pin.value(0)  # No interrupt
pin.value(1)  # Triggers interrupt (rising edge)
```

### SPI Communication

```python
import mock_machine
mock_machine.register_as_machine()
import machine

# Create SPI bus
spi = machine.SPI(0)

# Set up mock responses
spi.read_buf = b'\x01\x02\x03\x04'

# Test your SPI driver
data = spi.read(4)
assert data == b'\x01\x02\x03\x04'

# Check what was written
spi.write(b'\xAA\xBB')
assert spi.write_buf == b'\xAA\xBB'
```

## Examples

The `examples/` directory contains sample drivers with tests:
- `hardware_revision.py` - Reading hardware revision from I2C EEPROM
- `tmp117.py` - TMP117 temperature sensor driver with I2C communication

## Testing

Run the unit tests:

```bash
# Run all tests
python -m pytest test/

# Run specific test
python -m pytest test/test_mock_machine.py::test_i2c_scan
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2020-2024 Planet Innovation Pty Ltd

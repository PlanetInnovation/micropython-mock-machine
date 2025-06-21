# Quick Start Guide

This guide will help you get started with micropython-mock-machine in just a few minutes.

## Basic Setup

The fundamental concept is simple: replace the real `machine` module with our mock version:

```python
import mock_machine

# This replaces 'machine' in sys.modules
mock_machine.register_as_machine()

# Now any import of machine uses the mock
import machine
```

!!! warning "Import Order"
    Always call `register_as_machine()` before importing any modules that use `machine`.

## Your First Mock Test

Let's write a simple test for a function that reads a button:

```python
# button.py - Your production code
import machine

def is_button_pressed(pin_number):
    """Check if a button connected to a pin is pressed."""
    pin = machine.Pin(pin_number, machine.Pin.IN, machine.Pin.PULL_UP)
    return pin.value() == 0  # Active low

# test_button.py - Your test code
import mock_machine
mock_machine.register_as_machine()

from button import is_button_pressed

def test_button_press():
    # Get the mock pin object
    pin = mock_machine.Pin.pins[0]
    
    # Simulate button not pressed (high)
    pin.value(1)
    assert not is_button_pressed(0)
    
    # Simulate button pressed (low)
    pin.value(0)
    assert is_button_pressed(0)
```

## Testing I2C Devices

Here's how to test a simple I2C temperature sensor driver:

```python
# temp_sensor.py - Your driver code
import machine

class TempSensor:
    def __init__(self, i2c, addr=0x48):
        self.i2c = i2c
        self.addr = addr
    
    def read_temperature(self):
        # Read 2 bytes from register 0x00
        data = self.i2c.readfrom_mem(self.addr, 0x00, 2)
        # Convert to temperature (simplified)
        temp = (data[0] << 8) | data[1]
        return temp / 256.0

# test_temp_sensor.py - Your test code
import mock_machine
mock_machine.register_as_machine()

from mock_machine import I2C, I2CDevice
from temp_sensor import TempSensor

def test_temperature_reading():
    # Create mock I2C bus
    i2c = I2C(0)
    
    # Create mock device
    device = I2CDevice(addr=0x48, i2c=i2c)
    
    # Set temperature register to 25.5°C (0x19 0x80)
    device.register_values[0x00] = b'\x19\x80'
    
    # Test the driver
    sensor = TempSensor(i2c)
    temp = sensor.read_temperature()
    
    assert temp == 25.5
```

## Testing Interrupts

Test interrupt-driven code by simulating pin changes:

```python
# counter.py - Your production code
import machine

class EventCounter:
    def __init__(self, pin_number):
        self.count = 0
        self.pin = machine.Pin(pin_number, machine.Pin.IN)
        self.pin.irq(trigger=machine.Pin.IRQ_RISING, handler=self._increment)
    
    def _increment(self, pin):
        self.count += 1

# test_counter.py - Your test code
import mock_machine
mock_machine.register_as_machine()

from counter import EventCounter

def test_event_counting():
    counter = EventCounter(0)
    
    # Get the mock pin
    pin = mock_machine.Pin.pins[0]
    
    # Simulate events
    pin.value(0)  # Start low
    pin.value(1)  # Rising edge - triggers interrupt
    pin.value(0)  # Falling edge - no trigger
    pin.value(1)  # Rising edge - triggers interrupt
    
    # MicroPython schedules interrupts, so they may not be immediate
    import time
    time.sleep(0.1)
    
    assert counter.count == 2
```

## Common Patterns

### Pattern 1: Test Fixtures

Create reusable test fixtures:

```python
import pytest
import mock_machine

@pytest.fixture(autouse=True)
def mock_hardware():
    """Automatically mock hardware for all tests."""
    mock_machine.register_as_machine()
    yield
    # Clean up
    mock_machine.Pin.pins.clear()

@pytest.fixture
def mock_i2c():
    """Provide a mock I2C bus."""
    from mock_machine import I2C
    return I2C(0)
```

### Pattern 2: Device Factories

Create helper functions for common device setups:

```python
def create_mock_eeprom(i2c, addr=0x50, size=256):
    """Create a mock EEPROM device."""
    from mock_machine import I2CDevice
    device = I2CDevice(addr=addr, i2c=i2c)
    # Initialize with empty data
    for i in range(size):
        device.register_values[i] = b'\xFF'
    return device
```

### Pattern 3: Async Testing

Test asyncio-based code:

```python
import asyncio

async def test_async_sensor():
    # Your async test code here
    await asyncio.sleep(0.1)
    # Assertions...

# Run the test
asyncio.run(test_async_sensor())
```

## Next Steps

- Learn more about [Basic Usage](../guide/basic-usage.md)
- Explore [Testing Patterns](../guide/testing-patterns.md)
- See complete [Examples](../examples/i2c-testing.md)
- Read the [API Reference](../api/mock_machine.md)
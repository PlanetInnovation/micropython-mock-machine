# Overview

## Philosophy

micropython-mock-machine is designed with the following principles:

1. **Drop-in Replacement**: The mock should behave as close to the real `machine` module as possible
2. **Testability First**: Provide features that make testing easier, even if they don't exist in real hardware
3. **Predictable Behavior**: Mock behavior should be deterministic and controllable
4. **Zero Hardware Required**: All testing should be possible on any Python environment

## Architecture

### Module Registration

The core mechanism is replacing the `machine` module in Python's module system:

```python
import sys
sys.modules["machine"] = sys.modules["mock_machine"]
```

This is wrapped in the convenient `register_as_machine()` function. Once called, any subsequent `import machine` will load the mock module instead.

### Mock Object Lifecycle

Mock objects maintain state throughout their lifecycle:

```python
# Pin objects are singleton-like per pin number
pin1 = machine.Pin(0)
pin2 = machine.Pin(0)
assert pin1 is pin2  # Same object

# I2C devices are added to buses
i2c = machine.I2C(0)
device = I2CDevice(addr=0x50, i2c=i2c)
assert 0x50 in i2c.scan()  # Device is visible
```

### State Management

Each mock object manages its own state:

- **Pins**: Value, mode, pull resistor, interrupt handlers
- **I2C**: Connected devices, register values
- **SPI**: Read/write buffers, transaction history
- **ADC**: Simulated analog values
- **Timers**: Callback functions, periods
- **UART**: Input/output buffers

## Testing Workflow

A typical testing workflow with mock_machine:

1. **Setup Phase**
   ```python
   import mock_machine
   mock_machine.register_as_machine()
   ```

2. **Configuration Phase**
   ```python
   # Create mock hardware
   i2c = machine.I2C(0)
   device = I2CDevice(addr=0x68, i2c=i2c)
   device.register_values[0x00] = b'\x12\x34'
   ```

3. **Test Execution**
   ```python
   # Import and test your driver
   from my_driver import MyDevice
   dev = MyDevice(i2c)
   result = dev.read_data()
   ```

4. **Verification**
   ```python
   # Check interactions
   assert device.register_values[0x01] == b'\xFF'
   ```

## Key Differences from Real Hardware

While mock_machine strives for compatibility, some differences exist:

### Enhanced Testability Features

1. **Direct State Access**: You can directly read/write internal state
   ```python
   pin._value = 1  # Direct access for testing
   ```

2. **Device Addition**: I2C/SPI can have devices dynamically added
   ```python
   i2c.add_device(device)  # Not in real machine module
   ```

3. **Transaction History**: SPI tracks all transactions
   ```python
   spi.writes  # List of all written data
   ```

### Simplified Behavior

1. **No Timing**: Operations are instantaneous
2. **No Hardware Limits**: Unlimited devices, pins, etc.
3. **Perfect Reliability**: No communication errors unless simulated

## Integration with Test Frameworks

### unittest
```python
import unittest
import mock_machine

class TestMyDevice(unittest.TestCase):
    def setUp(self):
        mock_machine.register_as_machine()

    def test_device(self):
        # Your tests here
        pass
```

### pytest
```python
import pytest
import mock_machine

@pytest.fixture(autouse=True)
def mock_hardware():
    mock_machine.register_as_machine()
    yield
    mock_machine.Pin.pins.clear()
```

### asyncio
```python
import asyncio

async def test_async_operation():
    # Async test code
    await asyncio.sleep(0)

# Run with asyncio
asyncio.run(test_async_operation())
```

## Performance Considerations

mock_machine is designed for testing, not performance:

- Operations are synchronous (except where asyncio is used)
- No optimization for large data transfers
- Memory usage grows with stored state

For performance testing, consider:
- Limiting transaction history
- Clearing state between tests
- Using minimal mock features needed

## Next Steps

- Learn about [Basic Usage](basic-usage.md)
- Explore [Testing Patterns](testing-patterns.md)
- See [Advanced Topics](advanced.md)

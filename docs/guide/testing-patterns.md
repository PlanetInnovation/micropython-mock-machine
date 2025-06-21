# Testing Patterns

This guide presents common patterns and best practices for testing with mock_machine.

## Test Structure Patterns

### Pattern 1: Setup and Teardown

Always ensure clean state between tests:

```python
import unittest
import mock_machine

class TestMyDevice(unittest.TestCase):
    def setUp(self):
        # Register mock_machine
        mock_machine.register_as_machine()
        # Clear any existing state
        mock_machine.Pin.pins.clear()
        
    def tearDown(self):
        # Clean up after each test
        mock_machine.Pin.pins.clear()
        # Reset any global state
```

### Pattern 2: Pytest Fixtures

Use fixtures for reusable test setup:

```python
import pytest
import mock_machine

@pytest.fixture
def mock_i2c():
    """Provides a clean I2C bus for each test."""
    mock_machine.register_as_machine()
    from mock_machine import I2C
    return I2C(0)

@pytest.fixture
def temperature_sensor(mock_i2c):
    """Provides a mock temperature sensor."""
    from mock_machine import I2CDevice
    device = I2CDevice(addr=0x48, i2c=mock_i2c)
    device.register_values[0x00] = b'\x19\x00'  # 25°C
    return device

def test_read_temperature(mock_i2c, temperature_sensor):
    # Test uses pre-configured fixtures
    data = mock_i2c.readfrom_mem(0x48, 0x00, 2)
    assert data == b'\x19\x00'
```

## Device Simulation Patterns

### Pattern 3: Stateful Device Simulation

Create devices that maintain state across operations:

```python
class MockEEPROM(I2CDevice):
    """Simulates an I2C EEPROM with persistent storage."""
    
    def __init__(self, addr, i2c, size=256):
        super().__init__(addr, i2c)
        self.size = size
        self.memory = bytearray(size)
        self.current_address = 0
        
    def writeto(self, buf, stop=True):
        """Handle address write followed by data write."""
        if len(buf) == 1:
            # Address write
            self.current_address = buf[0]
        else:
            # Data write
            addr = buf[0]
            data = buf[1:]
            for i, byte in enumerate(data):
                if addr + i < self.size:
                    self.memory[addr + i] = byte
        return len(buf)
    
    def readfrom(self, nbytes, stop=True):
        """Read from current address."""
        data = bytes(self.memory[self.current_address:self.current_address + nbytes])
        self.current_address = (self.current_address + nbytes) % self.size
        return data
```

### Pattern 4: Error Injection

Test error handling by simulating failures:

```python
class UnreliableI2CDevice(I2CDevice):
    """Simulates an I2C device that occasionally fails."""
    
    def __init__(self, addr, i2c, failure_rate=0.1):
        super().__init__(addr, i2c)
        self.failure_rate = failure_rate
        self.call_count = 0
        
    def readfrom_mem(self, memaddr, nbytes):
        self.call_count += 1
        # Fail every N calls based on failure rate
        if self.call_count % int(1/self.failure_rate) == 0:
            raise OSError(errno.EIO, "I2C communication error")
        return super().readfrom_mem(memaddr, nbytes)

# Test error handling
def test_device_retry_logic():
    i2c = I2C(0)
    device = UnreliableI2CDevice(addr=0x50, i2c=i2c)
    device.register_values[0x00] = b'\x42'
    
    # Your driver should handle retries
    driver = MyDriver(i2c, addr=0x50)
    result = driver.read_with_retry(register=0x00)
    assert result == 0x42
```

## Interrupt Testing Patterns

### Pattern 5: Interrupt Verification

Test interrupt-driven code systematically:

```python
class InterruptCounter:
    def __init__(self):
        self.events = []
        
    def create_handler(self, name):
        def handler(pin):
            self.events.append((name, pin.value()))
        return handler

def test_button_debouncing():
    counter = InterruptCounter()
    
    # Create button with debouncing
    button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    button.irq(
        trigger=machine.Pin.IRQ_FALLING,
        handler=counter.create_handler("button")
    )
    
    # Simulate bouncy button press
    button.value(1)  # Released
    button.value(0)  # Pressed
    button.value(1)  # Bounce
    button.value(0)  # Bounce
    
    # Allow interrupts to process
    import time
    time.sleep(0.01)
    
    # Verify debouncing worked
    # (Implementation dependent on your debouncing logic)
    assert len(counter.events) >= 2
```

### Pattern 6: Async Event Testing

Test asynchronous event handling:

```python
import asyncio

async def test_async_pin_events():
    events = asyncio.Queue()
    
    async def pin_monitor(pin_num):
        pin = machine.Pin(pin_num, machine.Pin.IN)
        last_value = pin.value()
        
        while True:
            current_value = pin.value()
            if current_value != last_value:
                await events.put((pin_num, current_value))
                last_value = current_value
            await asyncio.sleep(0.01)
    
    # Start monitoring
    monitor_task = asyncio.create_task(pin_monitor(0))
    
    # Simulate pin changes
    pin = mock_machine.Pin.pins[0]
    pin.value(0)
    await asyncio.sleep(0.02)
    pin.value(1)
    await asyncio.sleep(0.02)
    
    # Check events
    event1 = await events.get()
    event2 = await events.get()
    
    assert event1 == (0, 0)
    assert event2 == (0, 1)
    
    monitor_task.cancel()
```

## Communication Testing Patterns

### Pattern 7: Protocol Verification

Verify correct protocol implementation:

```python
def test_spi_protocol():
    spi = machine.SPI(0)
    spi.writes = []  # Clear history
    
    # Test chip select protocol
    cs_pin = machine.Pin(10, machine.Pin.OUT, value=1)
    
    # Simulate SPI transaction
    cs_pin.low()  # Select chip
    spi.write(b'\x9F')  # Read ID command
    response = spi.read(3)  # Read 3 bytes
    cs_pin.high()  # Deselect chip
    
    # Verify protocol
    assert cs_pin.value() == 1  # CS is high (inactive)
    assert spi.writes == [b'\x9F']  # Correct command sent
```

### Pattern 8: Multi-Device Bus Testing

Test multiple devices on the same bus:

```python
def test_i2c_bus_sharing():
    i2c = I2C(0)
    
    # Add multiple devices
    eeprom = I2CDevice(addr=0x50, i2c=i2c)
    sensor = I2CDevice(addr=0x68, i2c=i2c)
    rtc = I2CDevice(addr=0x51, i2c=i2c)
    
    # Set up different responses
    eeprom.register_values[0x00] = b'\xEE'
    sensor.register_values[0x00] = b'\x55'
    rtc.register_values[0x00] = b'\xAA'
    
    # Verify bus scan sees all devices
    devices = i2c.scan()
    assert sorted(devices) == [0x50, 0x51, 0x68]
    
    # Verify independent communication
    assert i2c.readfrom_mem(0x50, 0x00, 1) == b'\xEE'
    assert i2c.readfrom_mem(0x68, 0x00, 1) == b'\x55'
    assert i2c.readfrom_mem(0x51, 0x00, 1) == b'\xAA'
```

## Performance Testing Patterns

### Pattern 9: Timing Verification

Test timing-sensitive code:

```python
import time

def test_periodic_sampling():
    samples = []
    sample_times = []
    
    def sample_callback(timer):
        samples.append(adc.read_u16())
        sample_times.append(time.time())
    
    # Set up ADC with changing values
    adc = machine.ADC(machine.Pin(0))
    
    # Start periodic sampling
    timer = machine.Timer(0)
    timer.init(mode=machine.Timer.PERIODIC, period=100, callback=sample_callback)
    
    # Simulate changing ADC values
    for i in range(10):
        mock_machine.ADC.pin_adc_map[mock_machine.Pin.pins[0]] = i * 1000
        time.sleep(0.05)
    
    timer.deinit()
    
    # Verify sampling occurred
    assert len(samples) >= 5
    assert samples[0] != samples[-1]  # Values changed
```

## Best Practices

### 1. Isolate Tests
Each test should be independent:
```python
def test_one():
    # This test's state...
    pass

def test_two():
    # ...should not affect this test
    pass
```

### 2. Use Meaningful Test Data
```python
# Good: Clear what the values represent
device.register_values[0x75] = b'\x68'  # WHO_AM_I = MPU6050 ID

# Bad: Magic numbers
device.register_values[0x75] = b'\x68'
```

### 3. Test Edge Cases
```python
def test_i2c_device_not_found():
    i2c = I2C(0)
    # No device at 0x99
    with pytest.raises(OSError):
        i2c.readfrom(0x99, 1)
```

### 4. Document Test Intent
```python
def test_temperature_sensor_negative_values():
    """Verify the sensor correctly handles negative temperatures."""
    # Test implementation
```

## Next Steps

- Explore [Advanced Topics](advanced.md) for complex scenarios
- See [Complete Examples](../examples/complete-suite.md) for full test suites
- Check the [API Reference](../api/mock_machine.md) for detailed documentation
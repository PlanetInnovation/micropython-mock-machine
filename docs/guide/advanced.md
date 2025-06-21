# Advanced Topics

This guide covers advanced usage scenarios and techniques for mock_machine.

## Custom Mock Implementations

### Extending Mock Classes

Create specialized mock devices by extending base classes:

```python
from mock_machine import I2CDevice
import struct

class MockIMU(I2CDevice):
    """Mock 6-axis IMU with accelerometer and gyroscope."""
    
    def __init__(self, addr, i2c):
        super().__init__(addr, i2c)
        # Initialize registers
        self.register_values[0x75] = b'\x68'  # WHO_AM_I
        self.accel = [0.0, 0.0, 9.81]  # Default to 1g on Z
        self.gyro = [0.0, 0.0, 0.0]
        self.temp = 25.0
        
    def readfrom_mem(self, memaddr, nbytes):
        if memaddr == 0x3B and nbytes >= 14:
            # Read all sensor data
            data = bytearray()
            # Pack accelerometer data (±2g range, 16384 LSB/g)
            for axis in self.accel:
                raw = int(axis * 16384)
                data.extend(struct.pack('>h', raw))
            # Pack temperature (340 LSB/°C, offset 36.53°C)
            temp_raw = int((self.temp - 36.53) * 340)
            data.extend(struct.pack('>h', temp_raw))
            # Pack gyroscope data (±250°/s range, 131 LSB/°/s)
            for axis in self.gyro:
                raw = int(axis * 131)
                data.extend(struct.pack('>h', raw))
            return bytes(data[:nbytes])
        return super().readfrom_mem(memaddr, nbytes)
    
    def simulate_motion(self, accel, gyro):
        """Simulate motion with given acceleration and gyro values."""
        self.accel = accel
        self.gyro = gyro
```

### Dynamic Behavior Simulation

Implement time-varying or state-dependent behavior:

```python
import time

class MockBattery(I2CDevice):
    """Simulates a battery fuel gauge with discharge over time."""
    
    def __init__(self, addr, i2c, capacity_mah=2000):
        super().__init__(addr, i2c)
        self.capacity_mah = capacity_mah
        self.current_mah = capacity_mah
        self.voltage = 4.2  # Fully charged
        self.start_time = time.time()
        self.discharge_rate = 100  # mA
        
    def readfrom_mem(self, memaddr, nbytes):
        # Update battery state based on time
        elapsed = time.time() - self.start_time
        discharged = (elapsed * self.discharge_rate) / 3600  # mAh
        self.current_mah = max(0, self.capacity_mah - discharged)
        
        # Update voltage based on charge
        soc = self.current_mah / self.capacity_mah
        self.voltage = 3.0 + (1.2 * soc)  # Linear approximation
        
        if memaddr == 0x04:  # Voltage register
            voltage_mv = int(self.voltage * 1000)
            return struct.pack('>H', voltage_mv)
        elif memaddr == 0x0C:  # State of charge
            soc_percent = int(soc * 100)
            return bytes([soc_percent])
        
        return super().readfrom_mem(memaddr, nbytes)
```

## Async Testing Patterns

### Testing Async Drivers

Test drivers that use asyncio:

```python
import asyncio

class AsyncI2CDriver:
    """Example async driver."""
    
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr
        
    async def read_sensor_async(self):
        # Simulate async operation
        await asyncio.sleep(0.01)
        data = self.i2c.readfrom_mem(self.addr, 0x00, 2)
        return struct.unpack('>H', data)[0]

async def test_async_driver():
    # Setup
    i2c = I2C(0)
    device = I2CDevice(addr=0x48, i2c=i2c)
    device.register_values[0x00] = b'\x12\x34'
    
    # Test async driver
    driver = AsyncI2CDriver(i2c, 0x48)
    value = await driver.read_sensor_async()
    assert value == 0x1234

# Run test
asyncio.run(test_async_driver())
```

### Async Event Streams

Create async generators for event streams:

```python
async def pin_event_stream(pin_num):
    """Generate events when pin changes."""
    pin = machine.Pin(pin_num, machine.Pin.IN)
    last_value = pin.value()
    
    while True:
        current_value = pin.value()
        if current_value != last_value:
            yield ('change', current_value)
            last_value = current_value
        await asyncio.sleep(0.001)

async def test_event_stream():
    # Create event stream
    events = pin_event_stream(0)
    
    # Collect events in background
    collected = []
    async def collector():
        async for event in events:
            collected.append(event)
            if len(collected) >= 3:
                break
    
    # Start collector
    task = asyncio.create_task(collector())
    
    # Generate events
    pin = mock_machine.Pin.pins[0]
    await asyncio.sleep(0.01)
    pin.value(1)
    await asyncio.sleep(0.01)
    pin.value(0)
    await asyncio.sleep(0.01)
    pin.value(1)
    
    # Wait for collection
    await task
    
    assert collected == [
        ('change', 1),
        ('change', 0),
        ('change', 1)
    ]
```

## Complex State Machines

### Testing State Machines

Test complex state-driven behavior:

```python
class DeviceStateMachine:
    """Example state machine for a device."""
    
    IDLE = 0
    INITIALIZING = 1
    READY = 2
    ERROR = 3
    
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr
        self.state = self.IDLE
        
    def initialize(self):
        self.state = self.INITIALIZING
        try:
            # Check device ID
            who_am_i = self.i2c.readfrom_mem(self.addr, 0x75, 1)
            if who_am_i != b'\x68':
                self.state = self.ERROR
                return False
            
            # Configure device
            self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')  # Wake up
            self.state = self.READY
            return True
        except OSError:
            self.state = self.ERROR
            return False

def test_state_machine_success():
    i2c = I2C(0)
    device = I2CDevice(addr=0x68, i2c=i2c)
    device.register_values[0x75] = b'\x68'  # Correct ID
    
    sm = DeviceStateMachine(i2c, 0x68)
    assert sm.state == sm.IDLE
    
    result = sm.initialize()
    assert result is True
    assert sm.state == sm.READY
    assert device.register_values[0x6B] == b'\x00'

def test_state_machine_wrong_id():
    i2c = I2C(0)
    device = I2CDevice(addr=0x68, i2c=i2c)
    device.register_values[0x75] = b'\x69'  # Wrong ID
    
    sm = DeviceStateMachine(i2c, 0x68)
    result = sm.initialize()
    assert result is False
    assert sm.state == sm.ERROR
```

## Memory and Performance Testing

### Testing Memory Constraints

Simulate memory-constrained environments:

```python
import gc

def test_memory_usage():
    # Force garbage collection
    gc.collect()
    
    # Record initial memory
    initial_free = gc.mem_free()
    
    # Create objects
    pins = []
    for i in range(100):
        pins.append(machine.Pin(i, machine.Pin.OUT))
    
    # Check memory usage
    gc.collect()
    after_create = gc.mem_free()
    
    # Clean up
    pins.clear()
    mock_machine.Pin.pins.clear()
    gc.collect()
    
    # Verify memory recovered
    after_cleanup = gc.mem_free()
    
    # Memory should be mostly recovered
    assert after_cleanup > after_create
```

### Performance Profiling

Profile mock operations:

```python
import time

def profile_i2c_operations():
    i2c = I2C(0)
    device = I2CDevice(addr=0x50, i2c=i2c)
    
    # Profile write operations
    start = time.time()
    for i in range(1000):
        i2c.writeto_mem(0x50, i % 256, bytes([i % 256]))
    write_time = time.time() - start
    
    # Profile read operations
    start = time.time()
    for i in range(1000):
        data = i2c.readfrom_mem(0x50, i % 256, 1)
    read_time = time.time() - start
    
    print(f"1000 writes: {write_time:.3f}s")
    print(f"1000 reads: {read_time:.3f}s")
```

## Integration Testing

### Testing Multiple Components

Test interactions between multiple hardware components:

```python
class SystemTest:
    """Integration test for a complete system."""
    
    def setup_hardware(self):
        # I2C devices
        self.i2c = I2C(0)
        self.imu = MockIMU(addr=0x68, i2c=self.i2c)
        self.eeprom = MockEEPROM(addr=0x50, i2c=self.i2c)
        
        # SPI devices
        self.spi = machine.SPI(0)
        self.spi.read_buf = b'\x01\x02\x03\x04'
        
        # GPIOs
        self.led = machine.Pin(0, machine.Pin.OUT)
        self.button = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
        
    def test_full_system(self):
        self.setup_hardware()
        
        # Simulate button press
        self.button.value(0)
        
        # System should:
        # 1. Turn on LED
        self.led.on()
        assert self.led.value() == 1
        
        # 2. Read IMU data
        self.imu.simulate_motion([1.0, 0.0, 9.81], [0.0, 0.0, 10.0])
        imu_data = self.i2c.readfrom_mem(0x68, 0x3B, 14)
        
        # 3. Store to EEPROM
        self.i2c.writeto_mem(0x50, 0x00, imu_data)
        
        # 4. Verify storage
        stored = self.i2c.readfrom_mem(0x50, 0x00, 14)
        assert stored == imu_data
```

## Debugging Techniques

### Mock Inspection

Inspect mock state for debugging:

```python
def debug_mock_state():
    """Print current mock state for debugging."""
    print("=== Mock Machine State ===")
    
    # Pin states
    print("\nPins:")
    for pin_id, pin in mock_machine.Pin.pins.items():
        print(f"  Pin {pin_id}: value={pin._value}, mode={pin._mode}")
    
    # I2C devices
    print("\nI2C Devices:")
    i2c = machine.I2C(0)
    for addr, device in i2c.devices.items():
        print(f"  Device 0x{addr:02X}: {type(device).__name__}")
        if hasattr(device, 'register_values'):
            for reg, val in device.register_values.items():
                print(f"    Reg 0x{reg:02X}: {val.hex()}")
```

### Transaction Logging

Log all hardware interactions:

```python
class LoggingI2C(I2C):
    """I2C bus that logs all operations."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = []
    
    def readfrom_mem(self, addr, memaddr, nbytes, *args, **kwargs):
        result = super().readfrom_mem(addr, memaddr, nbytes, *args, **kwargs)
        self.log.append(('read', addr, memaddr, nbytes, result))
        return result
    
    def writeto_mem(self, addr, memaddr, buf, *args, **kwargs):
        super().writeto_mem(addr, memaddr, buf, *args, **kwargs)
        self.log.append(('write', addr, memaddr, buf))
    
    def print_log(self):
        for entry in self.log:
            if entry[0] == 'read':
                _, addr, reg, nbytes, data = entry
                print(f"Read 0x{addr:02X}[0x{reg:02X}] -> {data.hex()}")
            else:
                _, addr, reg, data = entry
                print(f"Write 0x{addr:02X}[0x{reg:02X}] <- {data.hex()}")
```

## Best Practices for Advanced Usage

1. **Keep Mocks Simple**: Don't over-engineer mock behavior
2. **Document Assumptions**: Clearly state what the mock simulates
3. **Test the Tests**: Verify mock behavior matches real hardware
4. **Use Type Hints**: Help IDEs and static analyzers

```python
from typing import Optional, List

class MockDevice(I2CDevice):
    def __init__(self, addr: int, i2c: I2C) -> None:
        super().__init__(addr, i2c)
        self._data: Optional[bytes] = None
    
    def set_data(self, data: bytes) -> None:
        """Set the data to be returned by reads."""
        self._data = data
```

## Next Steps

- Review complete [Examples](../examples/complete-suite.md)
- Check the [API Reference](../api/mock_machine.md) for detailed documentation
- [Contribute](../contributing.md) your own mock implementations
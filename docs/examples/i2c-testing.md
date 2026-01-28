# I2C Device Testing Examples

This page provides comprehensive examples of testing I2C devices with mock_machine.

## Basic I2C Device Test

Testing a simple I2C temperature sensor:

```python
import mock_machine
mock_machine.register_as_machine()
import machine
from mock_machine import I2CDevice

class TempSensor:
    """Simple I2C temperature sensor driver."""

    def __init__(self, i2c, addr=0x48):
        self.i2c = i2c
        self.addr = addr

    def read_temperature(self):
        # Read 2 bytes from temperature register
        data = self.i2c.readfrom_mem(self.addr, 0x00, 2)
        # Convert to temperature (12-bit, 0.0625°C resolution)
        raw = (data[0] << 4) | (data[1] >> 4)
        if raw & 0x800:  # Sign bit
            raw = raw - 0x1000
        return raw * 0.0625

def test_temperature_sensor():
    # Create mock I2C bus
    i2c = machine.I2C(0)

    # Create mock device
    device = I2CDevice(addr=0x48, i2c=i2c)

    # Test positive temperature (25.5°C)
    # 25.5 / 0.0625 = 408 = 0x198
    device.register_values[0x00] = b'\x19\x80'

    sensor = TempSensor(i2c)
    temp = sensor.read_temperature()
    assert abs(temp - 25.5) < 0.1

    # Test negative temperature (-10°C)
    # -10 / 0.0625 = -160 = 0xF60 (two's complement)
    device.register_values[0x00] = b'\xF6\x00'

    temp = sensor.read_temperature()
    assert abs(temp - (-10.0)) < 0.1
```

## Multi-Register Device Test

Testing a device with multiple registers:

```python
class AccelerometerDriver:
    """Driver for I2C accelerometer."""

    REG_WHO_AM_I = 0x0F
    REG_CTRL1 = 0x20
    REG_OUT_X_L = 0x28

    def __init__(self, i2c, addr=0x19):
        self.i2c = i2c
        self.addr = addr

    def init(self):
        # Verify device ID
        who_am_i = self.i2c.readfrom_mem(self.addr, self.REG_WHO_AM_I, 1)[0]
        if who_am_i != 0x33:
            raise ValueError(f"Unknown device ID: 0x{who_am_i:02X}")

        # Enable all axes, 100Hz
        self.i2c.writeto_mem(self.addr, self.REG_CTRL1, b'\x57')

    def read_acceleration(self):
        # Read 6 bytes (X, Y, Z - each 2 bytes)
        data = self.i2c.readfrom_mem(self.addr, self.REG_OUT_X_L, 6)

        # Convert to signed 16-bit values
        x = int.from_bytes(data[0:2], 'little', signed=True)
        y = int.from_bytes(data[2:4], 'little', signed=True)
        z = int.from_bytes(data[4:6], 'little', signed=True)

        # Convert to g (±2g range, 16-bit)
        scale = 2.0 / 32768
        return (x * scale, y * scale, z * scale)

def test_accelerometer():
    i2c = machine.I2C(0)
    device = I2CDevice(addr=0x19, i2c=i2c)

    # Set up device registers
    device.register_values[0x0F] = b'\x33'  # WHO_AM_I

    # Test initialization
    accel = AccelerometerDriver(i2c)
    accel.init()

    # Verify configuration was written
    assert device.register_values[0x20] == b'\x57'

    # Set acceleration data (1g on Z axis)
    # 1g = 16384 counts in ±2g range
    device.register_values[0x28] = b'\x00\x00'  # X = 0
    device.register_values[0x2A] = b'\x00\x00'  # Y = 0
    device.register_values[0x2C] = b'\x00\x40'  # Z = 16384

    # Read acceleration
    x, y, z = accel.read_acceleration()
    assert abs(x) < 0.01
    assert abs(y) < 0.01
    assert abs(z - 1.0) < 0.01
```

## Device Discovery Test

Testing I2C bus scanning and device discovery:

```python
class I2CDeviceManager:
    """Manages multiple I2C devices on a bus."""

    KNOWN_DEVICES = {
        0x48: "Temperature Sensor",
        0x50: "EEPROM",
        0x68: "RTC/IMU",
        0x76: "Pressure Sensor",
    }

    def __init__(self, i2c):
        self.i2c = i2c
        self.devices = {}

    def scan_bus(self):
        """Scan for devices and identify them."""
        found = self.i2c.scan()

        for addr in found:
            if addr in self.KNOWN_DEVICES:
                self.devices[addr] = self.KNOWN_DEVICES[addr]
            else:
                self.devices[addr] = f"Unknown (0x{addr:02X})"

        return self.devices

def test_device_discovery():
    i2c = machine.I2C(0)

    # Add various mock devices
    temp_sensor = I2CDevice(addr=0x48, i2c=i2c)
    eeprom = I2CDevice(addr=0x50, i2c=i2c)
    rtc = I2CDevice(addr=0x68, i2c=i2c)
    unknown = I2CDevice(addr=0x3C, i2c=i2c)  # Unknown device

    # Test device manager
    manager = I2CDeviceManager(i2c)
    devices = manager.scan_bus()

    assert len(devices) == 4
    assert devices[0x48] == "Temperature Sensor"
    assert devices[0x50] == "EEPROM"
    assert devices[0x68] == "RTC/IMU"
    assert devices[0x3C] == "Unknown (0x3C)"
```

## EEPROM Read/Write Test

Testing EEPROM-style devices with address pointers:

```python
class EEPROM:
    """I2C EEPROM driver with page write support."""

    def __init__(self, i2c, addr=0x50, page_size=64):
        self.i2c = i2c
        self.addr = addr
        self.page_size = page_size

    def write_byte(self, mem_addr, data):
        """Write single byte to address."""
        self.i2c.writeto_mem(self.addr, mem_addr, bytes([data]))

    def read_byte(self, mem_addr):
        """Read single byte from address."""
        return self.i2c.readfrom_mem(self.addr, mem_addr, 1)[0]

    def write_page(self, mem_addr, data):
        """Write up to one page of data."""
        if len(data) > self.page_size:
            raise ValueError(f"Data exceeds page size ({self.page_size})")

        # Ensure we don't cross page boundary
        page_offset = mem_addr % self.page_size
        write_len = min(len(data), self.page_size - page_offset)

        self.i2c.writeto_mem(self.addr, mem_addr, data[:write_len])
        return write_len

    def read_sequential(self, mem_addr, length):
        """Read sequential data."""
        return self.i2c.readfrom_mem(self.addr, mem_addr, length)

def test_eeprom_operations():
    i2c = machine.I2C(0)
    device = I2CDevice(addr=0x50, i2c=i2c)

    eeprom = EEPROM(i2c)

    # Test single byte write/read
    eeprom.write_byte(0x00, 0x42)
    assert device.register_values[0x00] == b'\x42'
    assert eeprom.read_byte(0x00) == 0x42

    # Test page write
    test_data = b'Hello, EEPROM!'
    eeprom.write_page(0x10, test_data)
    assert device.register_values[0x10] == test_data

    # Test sequential read
    read_data = eeprom.read_sequential(0x10, len(test_data))
    assert read_data == test_data

    # Test page boundary
    # Writing at end of page should be limited
    written = eeprom.write_page(60, b'12345678')  # Page size = 64
    assert written == 4  # Only 4 bytes fit in page
```

## Error Handling Test

Testing I2C error conditions:

```python
class RobustI2CDevice:
    """I2C device driver with retry logic."""

    def __init__(self, i2c, addr, max_retries=3):
        self.i2c = i2c
        self.addr = addr
        self.max_retries = max_retries

    def read_with_retry(self, register, length):
        """Read with automatic retry on failure."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return self.i2c.readfrom_mem(self.addr, register, length)
            except OSError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Wait before retry (in real code)
                    pass

        raise last_error

    def verify_communication(self):
        """Verify device is responding."""
        try:
            devices = self.i2c.scan()
            return self.addr in devices
        except Exception:
            return False

def test_i2c_error_handling():
    i2c = machine.I2C(0)

    # Test device not present
    device = RobustI2CDevice(i2c, addr=0x99)

    # Should not find device
    assert not device.verify_communication()

    # Should raise error after retries
    with pytest.raises(OSError):
        device.read_with_retry(0x00, 1)

    # Add device and test success
    mock_device = I2CDevice(addr=0x99, i2c=i2c)
    mock_device.register_values[0x00] = b'\x55'

    assert device.verify_communication()
    data = device.read_with_retry(0x00, 1)
    assert data == b'\x55'
```

## Async I2C Test

Testing asynchronous I2C operations:

```python
import asyncio

class AsyncI2CSensor:
    """Async I2C sensor with periodic reading."""

    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr
        self.running = False

    async def start_monitoring(self, callback, interval=1.0):
        """Start periodic sensor reading."""
        self.running = True

        while self.running:
            try:
                # Read sensor data
                data = self.i2c.readfrom_mem(self.addr, 0x00, 2)
                value = (data[0] << 8) | data[1]

                # Call callback with value
                await callback(value)

            except OSError:
                # Handle communication error
                await callback(None)

            await asyncio.sleep(interval)

    def stop_monitoring(self):
        """Stop monitoring."""
        self.running = False

async def test_async_sensor():
    i2c = machine.I2C(0)
    device = I2CDevice(addr=0x40, i2c=i2c)

    # Simulate changing sensor values
    values = [0x1234, 0x2345, 0x3456]
    value_index = 0

    def update_sensor():
        nonlocal value_index
        val = values[value_index % len(values)]
        device.register_values[0x00] = bytes([val >> 8, val & 0xFF])
        value_index += 1

    # Collect readings
    readings = []

    async def handle_reading(value):
        readings.append(value)
        update_sensor()  # Change value for next read

    # Start monitoring
    sensor = AsyncI2CSensor(i2c, 0x40)
    update_sensor()  # Set initial value

    # Run for a short time
    monitor_task = asyncio.create_task(
        sensor.start_monitoring(handle_reading, interval=0.1)
    )

    await asyncio.sleep(0.35)
    sensor.stop_monitoring()
    await monitor_task

    # Verify readings
    assert len(readings) >= 3
    assert readings[0] == 0x1234
    assert readings[1] == 0x2345
    assert readings[2] == 0x3456

# Run async test
asyncio.run(test_async_sensor())
```

## Best Practices

1. **Always Mock at Appropriate Level**: Mock I2C devices, not individual methods
2. **Use Realistic Values**: Use actual register addresses and data formats
3. **Test Edge Cases**: Empty responses, communication errors, boundary values
4. **Document Register Maps**: Clearly document what each register represents
5. **Verify Protocol Compliance**: Ensure your mock follows I2C specifications

## Common Pitfalls

- **Forgetting to Add Device**: Device must be added to bus before use
- **Wrong Data Types**: Register values must be bytes, not integers
- **Address Conflicts**: Each device needs a unique address
- **Timing Assumptions**: Mock operations are instantaneous

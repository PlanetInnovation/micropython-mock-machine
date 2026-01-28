# Device Classes

This page documents the mock device helper classes that make it easier to simulate hardware devices.

## I2CDevice

::: mock_machine.I2CDevice
    options:
      show_source: true
      members:
        - __init__
        - readfrom
        - readfrom_into
        - writeto
        - readfrom_mem
        - readfrom_mem_into
        - writeto_mem

The `I2CDevice` class is a helper for simulating I2C devices. It automatically registers itself with the I2C bus when created.

### Basic Usage

```python
from mock_machine import I2C, I2CDevice

# Create bus and device
i2c = I2C(0)
device = I2CDevice(addr=0x68, i2c=i2c)

# Set register values
device.register_values[0x75] = b'\x68'  # WHO_AM_I register

# Device is now accessible via I2C
data = i2c.readfrom_mem(0x68, 0x75, 1)
assert data == b'\x68'
```

### Extending I2CDevice

Create custom device simulations by extending `I2CDevice`:

```python
class MockSensor(I2CDevice):
    def __init__(self, addr, i2c):
        super().__init__(addr, i2c)
        # Initialize with default values
        self.temperature = 25.0
        self.register_values[0x00] = self._encode_temp()

    def _encode_temp(self):
        # Convert temperature to bytes
        raw = int(self.temperature * 100)
        return bytes([raw >> 8, raw & 0xFF])

    def writeto_mem(self, memaddr, buf):
        if memaddr == 0x01:  # Config register
            # Handle configuration changes
            self.config = buf[0]
        super().writeto_mem(memaddr, buf)

    def set_temperature(self, temp):
        self.temperature = temp
        self.register_values[0x00] = self._encode_temp()
```

## Memory Class

::: mock_machine.Memory
    options:
      show_source: true
      members:
        - __init__
        - __getitem__

The `Memory` class provides memory-mapped I/O simulation for `mem8`, `mem16`, and `mem32`.

### Usage

```python
# Memory objects are pre-created
from mock_machine import mem8, mem16, mem32

# Read memory (returns fixed values)
byte_val = mem8[0x1000]    # Returns 0xFF
word_val = mem16[0x1000]   # Returns 0xFFFF
dword_val = mem32[0x1000]  # Returns 0xFFFFFFFF
```

## Creating Custom Mock Devices

### Best Practices

1. **Inherit from Base Classes**: Extend `I2CDevice` for I2C devices
2. **Initialize Registers**: Set default register values in `__init__`
3. **Override Methods**: Customize behavior by overriding read/write methods
4. **Document Behavior**: Clearly document what your mock simulates

### Example: Mock RTC Device

```python
import struct
import time

class MockRTC(I2CDevice):
    """Mock DS3231 RTC device."""

    def __init__(self, addr=0x68, i2c=None):
        super().__init__(addr, i2c)
        self.time_offset = 0

    def readfrom_mem(self, memaddr, nbytes):
        if memaddr == 0x00 and nbytes >= 7:
            # Return current time as BCD
            t = time.localtime(time.time() + self.time_offset)
            data = bytearray([
                self._to_bcd(t[5]),      # Seconds
                self._to_bcd(t[4]),      # Minutes
                self._to_bcd(t[3]),      # Hours
                self._to_bcd(t[6] + 1),  # Day of week
                self._to_bcd(t[2]),      # Date
                self._to_bcd(t[1]),      # Month
                self._to_bcd(t[0] % 100) # Year
            ])
            return bytes(data[:nbytes])
        return super().readfrom_mem(memaddr, nbytes)

    def writeto_mem(self, memaddr, buf):
        if memaddr == 0x00 and len(buf) >= 7:
            # Set time from BCD values
            # (Implementation would decode BCD and set time_offset)
            pass
        super().writeto_mem(memaddr, buf)

    @staticmethod
    def _to_bcd(val):
        """Convert value to BCD format."""
        return ((val // 10) << 4) | (val % 10)
```

### Example: Mock SPI Flash

```python
class MockSPIFlash:
    """Mock SPI flash memory device."""

    def __init__(self, spi, cs_pin, size=1024*1024):
        self.spi = spi
        self.cs = cs_pin
        self.size = size
        self.memory = bytearray(size)
        self.commands = {
            0x9F: self._jedec_id,
            0x03: self._read_data,
            0x02: self._page_program,
            0x20: self._sector_erase,
        }

    def _jedec_id(self, data):
        """Return JEDEC ID."""
        return b'\xEF\x40\x14'  # Example: W25Q80

    def _read_data(self, data):
        """Read data from address."""
        if len(data) >= 3:
            addr = (data[0] << 16) | (data[1] << 8) | data[2]
            # Return data from address
            # (Implementation would handle read)
        return b''

    def execute_command(self, cmd_data):
        """Execute SPI command."""
        if cmd_data[0] in self.commands:
            return self.commands[cmd_data[0]](cmd_data)
        return b''
```

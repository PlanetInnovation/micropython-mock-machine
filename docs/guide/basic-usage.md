# Basic Usage

This guide covers the fundamental usage patterns for each mock_machine component.

## Pin (GPIO)

### Basic Pin Operations

```python
import mock_machine
mock_machine.register_as_machine()
import machine

# Create output pin
pin_out = machine.Pin(0, machine.Pin.OUT)
pin_out.value(1)  # Set high
pin_out.on()      # Alternative way
pin_out.off()     # Set low

# Create input pin with pull-up
pin_in = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
value = pin_in.value()  # Read pin state
```

### Pin Modes and Configuration

```python
# Supported modes
pin = machine.Pin(0, machine.Pin.OUT)         # Output
pin = machine.Pin(1, machine.Pin.IN)          # Input
pin = machine.Pin(2, machine.Pin.OPEN_DRAIN)  # Open drain
pin = machine.Pin(3, machine.Pin.ALT)         # Alternate function

# Pull resistors
pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
pin = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Reconfigure existing pin
pin.init(mode=machine.Pin.OUT, pull=None)
```

### Accessing Mock Pin State

```python
# Get the mock pin object directly
mock_pin = mock_machine.Pin.pins[0]

# Set value for testing
mock_pin.value(1)

# Check internal state
assert mock_pin._mode == machine.Pin.OUT
assert mock_pin._value == 1
```

## I2C (Inter-Integrated Circuit)

### Basic I2C Operations

```python
# Create I2C bus
i2c = machine.I2C(0, scl=machine.Pin(0), sda=machine.Pin(1), freq=400000)

# Scan for devices
devices = i2c.scan()  # Returns list of addresses

# Read from device
data = i2c.readfrom(0x50, 10)  # Read 10 bytes from address 0x50

# Write to device
i2c.writeto(0x50, b'Hello')  # Write bytes to address 0x50

# Memory operations
data = i2c.readfrom_mem(0x50, 0x00, 4)  # Read 4 bytes from register 0x00
i2c.writeto_mem(0x50, 0x00, b'\x01\x02\x03\x04')  # Write to register
```

### Creating Mock I2C Devices

```python
from mock_machine import I2C, I2CDevice

# Create bus and device
i2c = I2C(0)
device = I2CDevice(addr=0x68, i2c=i2c)

# Set up register values
device.register_values[0x0D] = b'\x1A'  # WHO_AM_I register
device.register_values[0x00] = b'\x00\x00'  # Data register

# Device is now visible on bus
assert 0x68 in i2c.scan()

# Read from registers
who_am_i = i2c.readfrom_mem(0x68, 0x0D, 1)
assert who_am_i == b'\x1A'
```

### Advanced I2C Device Behavior

```python
class MockSensor(I2CDevice):
    """Custom I2C device with dynamic behavior."""

    def __init__(self, addr, i2c):
        super().__init__(addr, i2c)
        self.temperature = 25.0

    def readfrom_mem(self, memaddr, nbytes):
        if memaddr == 0x00:  # Temperature register
            # Convert temperature to bytes
            temp_raw = int(self.temperature * 256)
            return bytes([(temp_raw >> 8) & 0xFF, temp_raw & 0xFF])
        return super().readfrom_mem(memaddr, nbytes)

# Use custom device
i2c = I2C(0)
sensor = MockSensor(addr=0x48, i2c=i2c)
sensor.temperature = 26.5

data = i2c.readfrom_mem(0x48, 0x00, 2)
# data contains temperature as bytes
```

## SPI (Serial Peripheral Interface)

### Basic SPI Operations

```python
# Create SPI bus
spi = machine.SPI(0)
spi.init(baudrate=1000000, polarity=0, phase=0)

# Read operations
data = spi.read(10)  # Read 10 bytes
buffer = bytearray(10)
spi.readinto(buffer)  # Read into existing buffer

# Write operations
spi.write(b'Hello SPI')  # Write bytes

# Combined read/write
write_buf = b'\x01\x02\x03'
read_buf = bytearray(3)
spi.write_readinto(write_buf, read_buf)
```

### Configuring Mock SPI Responses

```python
# Set up read data
spi.read_buf = b'\x01\x02\x03\x04'
data = spi.read(4)  # Returns b'\x01\x02\x03\x04'

# Multiple different responses
spi.reads = [b'\xAA', b'\xBB', b'\xCC']
data1 = spi.read(1)  # Returns b'\xAA'
data2 = spi.read(1)  # Returns b'\xBB'
data3 = spi.read(1)  # Returns b'\xCC'

# Check what was written
spi.write(b'\x55\xAA')
assert spi.write_buf == b'\x55\xAA'
assert spi.writes == [b'\x55\xAA']  # History of all writes
```

## ADC (Analog to Digital Converter)

### Basic ADC Usage

```python
# Create ADC on a pin
adc = machine.ADC(machine.Pin(0))

# Read value (0-65535 for 16-bit)
value = adc.read_u16()
```

### Simulating ADC Values

```python
# Direct access to set ADC values
mock_machine.ADC.pin_adc_map[pin] = 32768  # Mid-scale

# Now reading returns the set value
adc = machine.ADC(pin)
assert adc.read_u16() == 32768

# Simulate changing values
for value in range(0, 65536, 1000):
    mock_machine.ADC.pin_adc_map[pin] = value
    reading = adc.read_u16()
    print(f"ADC reading: {reading}")
```

## UART (Serial Communication)

### Basic UART Operations

```python
# Create UART
uart = machine.UART(1)

# Write data
uart.write(b'Hello UART\n')

# Read data
data = uart.read(10)  # Read up to 10 bytes
line = uart.readline()  # Read until newline

# Check available data
if uart.any():
    data = uart.read()
```

### Simulating UART Communication

```python
# Create UART with pre-loaded read data
uart = mock_machine.UART(data_for_read=b'Response\n')

# Read the data
line = uart.readline()
assert line == b'Response\n'

# Check what was written
uart.write(b'Command\n')
uart.write_buf.seek(0)
written = uart.write_buf.read()
assert written == b'Command\n'
```

## Timer

### Basic Timer Usage

```python
# Create periodic timer
def timer_callback(timer):
    print("Timer fired!")

timer = machine.Timer(0)
timer.init(mode=machine.Timer.PERIODIC, period=1000, callback=timer_callback)

# Stop timer
timer.deinit()

# One-shot timer
timer.init(mode=machine.Timer.ONE_SHOT, period=5000, callback=timer_callback)
```

## PWM (Pulse Width Modulation)

### Basic PWM Usage

```python
# Create PWM on a pin
pwm = machine.PWM(machine.Pin(0), freq=1000, duty_u16=32768)

# Adjust frequency and duty cycle
pwm.freq(2000)  # 2kHz
pwm.duty_u16(16384)  # 25% duty cycle

# Read current values
current_freq = pwm.freq()
current_duty = pwm.duty_u16()
```

## RTC (Real Time Clock)

### Basic RTC Usage

```python
# Create RTC
rtc = machine.RTC()

# Set up wakeup alarm
def wakeup_callback():
    print("RTC wakeup!")

rtc.wakeup(timeout=5000, callback=wakeup_callback)

# Get datetime
datetime = rtc.datetime()
# Returns: (year, month, day, weekday, hour, minute, second, microsecond)
```

## Next Steps

Now that you understand the basic usage of each component:
- Learn about [Testing Patterns](testing-patterns.md) for effective test design
- Explore [Advanced Topics](advanced.md) for complex scenarios
- See complete [Examples](../examples/i2c-testing.md) for real-world usage

# micropython-mock-machine

Welcome to the documentation for micropython-mock-machine, a comprehensive mocking library for the MicroPython `machine` module.

## What is micropython-mock-machine?

micropython-mock-machine is a pure Python library that provides mock implementations of the MicroPython `machine` module's hardware interfaces. It enables you to:

- **Unit test** MicroPython drivers without physical hardware
- **Develop** MicroPython applications in a simulated environment
- **Verify** hardware interactions in continuous integration pipelines
- **Debug** complex hardware scenarios with predictable behavior

## Key Features

- **Complete API Coverage** - Implements all major `machine` module classes
- **Device Simulation** - Simulate multiple I2C/SPI devices on a single bus
- **Interrupt Support** - Test interrupt-driven code with simulated pin changes
- **Async Compatible** - Works seamlessly with MicroPython's asyncio
- **Zero Dependencies** - Pure Python implementation requiring only MicroPython core

## Quick Example

```python
import mock_machine

# Register mock_machine as the machine module
mock_machine.register_as_machine()

# Now use machine as normal
import machine

# Create and test hardware interfaces
i2c = machine.I2C(0)
pin = machine.Pin(0, machine.Pin.OUT)

# Your hardware interactions are now mocked
pin.value(1)
assert pin.value() == 1
```

## Supported Hardware

| Hardware | Status | Key Features |
|----------|--------|--------------|
| I2C | ✅ Full | Device simulation, register access |
| SPI | ✅ Full | Read/write buffers, sequential operations |
| Pin | ✅ Full | Interrupts, modes, pull resistors |
| ADC | ✅ Basic | 16-bit readings |
| PWM | ✅ Full | Frequency and duty cycle |
| UART | ✅ Full | Buffered I/O operations |
| Timer | ✅ Full | Periodic and one-shot modes |
| WDT | ✅ Full | Timeout detection |
| RTC | ✅ Full | Alarms and datetime |

## Getting Started

Ready to start testing your MicroPython hardware code? Head over to the [Installation Guide](getting-started/installation.md) to get micropython-mock-machine set up in your project.

## Project Information

micropython-mock-machine is developed and maintained by [Planet Innovation](https://planetinnovation.com.au/). It's released under the MIT license and welcomes contributions from the community.

- **Repository**: [GitHub](https://github.com/planetinnovation/micropython-mock-machine)
- **Issue Tracker**: [GitHub Issues](https://github.com/planetinnovation/micropython-mock-machine/issues)
- **License**: [MIT](https://github.com/planetinnovation/micropython-mock-machine/blob/main/LICENSE)

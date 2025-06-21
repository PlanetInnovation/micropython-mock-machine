# Installation

There are several ways to install micropython-mock-machine depending on your use case.

## Using mip (Recommended)

The easiest way to install micropython-mock-machine is using MicroPython's built-in package manager, `mip`:

```python
import mip
mip.install("github:planetinnovation/micropython-mock-machine")
```

This will download and install the latest version directly to your MicroPython device.

### Installing a specific version

```python
import mip
mip.install("github:planetinnovation/micropython-mock-machine", version="v1.0.0")
```

## Using mpremote

If you're working with a device connected to your computer, you can use `mpremote`:

```bash
mpremote mip install github:planetinnovation/micropython-mock-machine
```

## Manual Installation

For development or when working with the Unix port of MicroPython:

1. Clone the repository:
```bash
git clone https://github.com/planetinnovation/micropython-mock-machine.git
```

2. Copy `mock_machine.py` to your project:
```bash
cp micropython-mock-machine/mock_machine.py /path/to/your/project/lib/
```

## As a Git Submodule

For projects that need version control of dependencies:

```bash
git submodule add https://github.com/planetinnovation/micropython-mock-machine.git lib/mock_machine
```

## Development Installation

For contributing to micropython-mock-machine:

```bash
# Clone the repository
git clone https://github.com/planetinnovation/micropython-mock-machine.git
cd micropython-mock-machine

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## Verifying Installation

After installation, verify everything is working:

```python
import mock_machine

# Check version
print(mock_machine.__version__)

# Test basic functionality
mock_machine.register_as_machine()
import machine

pin = machine.Pin(0)
print("Installation successful!")
```

## Next Steps

Now that you have micropython-mock-machine installed, check out the [Quick Start Guide](quickstart.md) to begin using it in your tests.
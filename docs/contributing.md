# Contributing to micropython-mock-machine

We welcome contributions to micropython-mock-machine! This guide will help you get started.

## Getting Started

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/micropython-mock-machine.git
   cd micropython-mock-machine
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

3. **Run Tests**
   ```bash
   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=mock_machine
   ```

## Development Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/add-dac-support`
- `fix/i2c-scan-issue`
- `docs/improve-examples`

### 2. Make Your Changes

Follow the coding standards:
- Use type hints where possible
- Add docstrings to all public methods
- Follow existing code style
- Keep line length under 99 characters

### 3. Add Tests

All new features must include tests:

```python
def test_your_new_feature():
    """Test description of what you're testing."""
    # Arrange
    mock_machine.register_as_machine()

    # Act
    result = your_function()

    # Assert
    assert result == expected_value
```

### 4. Update Documentation

- Add docstrings to new classes/methods
- Update relevant documentation pages
- Add examples if introducing new features

### 5. Run Quality Checks

```bash
# Format code
ruff format mock_machine.py test/

# Lint code
ruff check mock_machine.py test/

# Type check
mypy mock_machine.py

# Run tests
pytest
```

### 6. Commit Your Changes

Write clear commit messages:
```bash
git add .
git commit -m "Add DAC support with 12-bit resolution

- Implement DAC class with write_u16 method
- Add tests for DAC voltage output
- Update documentation with DAC examples"
```

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Reference to any related issues
- Test results/coverage

## Guidelines

### Code Style

We use `ruff` for formatting and linting:

```python
# Good
class MockDevice(I2CDevice):
    """Mock device with clear purpose."""

    def __init__(self, addr: int, i2c: I2C) -> None:
        super().__init__(addr, i2c)
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize the device."""
        self._initialized = True
        return True

# Bad
class device:
    def __init__(self,addr,i2c):
        self.addr=addr
        self.i2c=i2c
```

### Testing Guidelines

1. **Test Isolation**: Each test should be independent
2. **Mock State**: Always clean up mock state after tests
3. **Edge Cases**: Test boundary conditions and error cases
4. **Documentation**: Document what each test verifies

Example test structure:
```python
class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        mock_machine.register_as_machine()
        self.device = MockDevice()

    def tearDown(self):
        """Clean up after test."""
        mock_machine.Pin.pins.clear()

    def test_normal_operation(self):
        """Test normal operation of feature."""
        # Test implementation

    def test_error_condition(self):
        """Test how feature handles errors."""
        # Test implementation
```

### Documentation Standards

- Use Google-style docstrings
- Include type hints in signatures
- Provide usage examples
- Document exceptions raised

```python
def read_sensor(addr: int, register: int, length: int) -> bytes:
    """Read data from sensor register.

    Args:
        addr: I2C address of the sensor
        register: Register address to read from
        length: Number of bytes to read

    Returns:
        Bytes read from the sensor

    Raises:
        OSError: If communication fails
        ValueError: If parameters are invalid

    Example:
        >>> data = read_sensor(0x68, 0x00, 2)
        >>> temperature = struct.unpack('>h', data)[0]
    """
```

## Adding New Mock Classes

When adding new hardware mocks:

1. **Study the Real API**: Check MicroPython documentation
2. **Implement Core Methods**: Start with essential functionality
3. **Add Helper Features**: Add testing-specific features
4. **Document Differences**: Note any deviations from real hardware

Template for new mock class:
```python
class NewHardware:
    """Mock implementation of NewHardware.

    Simulates the behavior of [hardware description].

    See: https://docs.micropython.org/en/latest/library/machine.NewHardware.html
    """

    def __init__(self, id, **kwargs):
        """Initialize the mock hardware."""
        self._id = id
        self._state = "initialized"
        # Store configuration

    def method(self, param):
        """Implement hardware method."""
        # Implementation

    # Testing helpers (not in real API)
    def _get_state(self):
        """Get internal state for testing."""
        return self._state
```

## Reporting Issues

When reporting issues, please include:

1. **Description**: Clear description of the problem
2. **Reproduction**: Minimal code to reproduce
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: Python version, OS, etc.

Example issue:
```markdown
## Description
I2C scan returns duplicate addresses when device is added twice

## Reproduction
```python
i2c = machine.I2C(0)
device = I2CDevice(addr=0x50, i2c=i2c)
device2 = I2CDevice(addr=0x50, i2c=i2c)  # Same address
print(i2c.scan())  # [80, 80] instead of error
```

## Expected Behavior
Should raise ValueError for duplicate address

## Environment
- Python 3.10
- micropython-mock-machine 1.0.0
```

## Questions?

- Open an issue for questions
- Check existing issues first
- Be respectful and constructive

Thank you for contributing to micropython-mock-machine!

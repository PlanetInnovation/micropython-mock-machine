# mock_machine Module

::: mock_machine.register_as_machine
    options:
      show_source: true

::: mock_machine.reset_cause
    options:
      show_source: true

## Constants

### Reset Causes

- `SOFT_RESET` = 0
- `PWRON_RESET` = 1
- `HARD_RESET` = 2
- `WDT_RESET` = 3
- `DEEPSLEEP_RESET` = 4

## Memory Access

::: mock_machine.mem8
    options:
      show_source: false

::: mock_machine.mem16
    options:
      show_source: false

::: mock_machine.mem32
    options:
      show_source: false
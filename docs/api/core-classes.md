# Core Classes

This page documents the core hardware interface classes provided by mock_machine.

## Pin

::: mock_machine.Pin
    options:
      show_source: true
      members:
        - __init__
        - init
        - value
        - on
        - off
        - high
        - low
        - irq
        - mode
        - __call__

### Pin Constants

- `Pin.IN` - Input mode
- `Pin.OUT` - Output mode
- `Pin.OPEN_DRAIN` - Open drain mode
- `Pin.ALT` - Alternate function mode
- `Pin.ALT_OPEN_DRAIN` - Alternate open drain mode
- `Pin.ANALOG` - Analog mode
- `Pin.PULL_UP` - Enable pull-up resistor
- `Pin.PULL_DOWN` - Enable pull-down resistor
- `Pin.IRQ_RISING` - Interrupt on rising edge
- `Pin.IRQ_FALLING` - Interrupt on falling edge

## I2C

::: mock_machine.I2C
    options:
      show_source: true
      members:
        - __init__
        - init
        - deinit
        - scan
        - readfrom
        - readfrom_into
        - writeto
        - readfrom_mem
        - readfrom_mem_into
        - writeto_mem
        - add_device

## SPI

::: mock_machine.SPI
    options:
      show_source: true
      members:
        - __init__
        - init
        - deinit
        - read
        - readinto
        - write
        - write_readinto
        - reset

## ADC

::: mock_machine.ADC
    options:
      show_source: true
      members:
        - __init__
        - init
        - block
        - read_u16
        - read_uv

## PWM

::: mock_machine.PWM
    options:
      show_source: true
      members:
        - __init__
        - init
        - deinit
        - freq
        - duty_u16
        - duty_ns

## UART

::: mock_machine.UART
    options:
      show_source: true
      members:
        - __init__
        - write
        - read
        - readinto
        - readline
        - seek
        - flush
        - close
        - any
        - ioctl

## Timer

::: mock_machine.Timer
    options:
      show_source: true
      members:
        - __init__
        - init
        - deinit

### Timer Constants

- `Timer.ONE_SHOT` - One-shot timer mode
- `Timer.PERIODIC` - Periodic timer mode

## WDT

::: mock_machine.WDT
    options:
      show_source: true
      members:
        - __init__
        - disable
        - feed

## RTC

::: mock_machine.RTC
    options:
      show_source: true
      members:
        - __init__
        - wakeup
        - stop
        - info
        - init
        - datetime

## Signal

::: mock_machine.Signal
    options:
      show_source: true
      members:
        - __init__
        - on
        - off
        - value
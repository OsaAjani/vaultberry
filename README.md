# Vaultberry - Raspberry Pi Powered Secure Vault System

Vaultberry is a secure vault system powered by Raspberry Pi, designed to provide a safe and convenient storage solution for your valuable items.

## Author

- Author: OsaAjani
- Date: 21 Feb 2024

## Installation

1. Connect the keypad, SG90 servo motor, and LCD display to the appropriate GPIO pins on the Raspberry Pi according to the wiring information provided below.

2. Clone the repository into the `/var/www/html/vaultberry` directory on your Raspberry Pi:

```bash
   git clone https://github.com/osaajani/vaultberry.git /var/www/html/vaultberry
   cd /var/www/html/vaultberry/ && ./install.sh
```

## Wiring Information

To set up Vaultberry, you'll need to wire the following components to the appropriate GPIO pins on the Raspberry Pi:

- **LCD**:
  - VCC: Pin 1 (3.3V)
  - GND: Pin 14 (Ground)
  - I2C: Pins 3 (SDA) & 5 (SCL)
  
- **Keypad**:
  - Rows: Pins 7, 11, 13, 15
  - Columns: Pins 16, 18, 22, 24
  
- **Servo Motor**:
  - PWM (Yellow): Pin 12 (GPIO18)
  - VCC (Red): Pin 4 (5V)
  - GND (Black/Brown): Pin 6 (Ground)

## Usage

The vaultberry.py script will be run automatically on startup, you just have to wait for boot to end then follow instructions on the vault screen.

#! /usr/bin/env python
"""
Vaultberry - Raspberry Pi Powered Secure Vault System

This script controls Vaultberry, a secure vault system powered by Raspberry Pi.
Vaultberry integrates a keypad for code input, an SG90 servo motor for the locking mechanism,
an LCD display for user interaction, and a custom-made lock mechanism.

Author: OsaAjani
Date: 21 feb 2024


Wiring Information:
- LCD: 
  - VCC: Pin 1 (3.3V)
  - GND: Pin 14 (Ground)
  - I2C: Pins 3 (SDA) & 5 (SCL)
- Keypad: 
  - Rows: Pins 7, 11, 13, 15
  - Columns: Pins 16, 18, 22, 24
- Servo Motor:
  - PWM (Yellow): Pin 12 (GPIO18)
  - VCC (Red): Pin 4 (5V)
  - GND (Black/Brown): Pin 6 (Ground)


Usage:
1. Connect the keypad, SG90 servo motor, and LCD display to the appropriate GPIO pins on the Raspberry Pi.
2. Run this script to initialize the Vaultberry system.
3. Follow the on-screen instructions to operate the vault, including entering codes on the keypad.

Note: This script is a part of the Vaultberry project and may require additional setup/configuration.
"""

from pad4pi import rpi_gpio
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import drivers
import time

CORRECT_CODE = "1234" # Code to open
CURRENT_CODE = ""
MASTER_CODE = "000000"
SHOW_CODE = False # If true show code in plaintext, else show *
# Configure LCD back light behaviour 
# If "on", light always on, if "auto" stop after 10s of inactivity, if "off" always off
LCD_BACKLIGHT = "auto" 

KEYPAD = [
    [1, 2, 3, "A"],
    [4, 5, 6, "B"],
    [7, 8, 9, "C"],
    ["*", 0, "#", "D"]
]

ROW_PINS = [4, 17, 27, 22] # BCM numbering
COL_PINS = [23, 24, 25, 8] # BCM numbering

STATE_INITIALIZE = 0
STATE_HOME = 1
STATE_ENTER_CODE = 2
STATE_INVALID_CODE = 4
STATE_VALID_CODE = 8
STATE_MASTER_CODE = 16
STATE_RESET_CODE_START = 32
STATE_RESET_CODE_END = 32

# Special codes that must trigger particular states
SPECIAL_CODES = {
    '##': STATE_MASTER_CODE,
}

LCD_BACKLIGHT_STATE = False if LCD_BACKLIGHT == "off" else True
PREVIOUS_STATE = STATE_INITIALIZE
CURRENT_STATE = STATE_INITIALIZE
LAST_ACTION_AT = time.time()


def update_state(new_state) :
    global CURRENT_STATE, PREVIOUS_STATE, LAST_ACTION_AT
    old = CURRENT_STATE
    PREVIOUS_STATE = CURRENT_STATE
    CURRENT_STATE = new_state
    LAST_ACTION_AT = time.time()
    return old


def cleanup_keypad() :
    global keypad
    keypad.cleanup()


def pprint(text, uppercase = True) :
    """ 
        Print on both stdout and lcd with auto linebreak translation 
        By default uppercase lcd string
    """
    display.lcd_clear()
    print(text)
    i = 1
    for line in text.split("\n") :
        display.lcd_display_string(line.upper(), i)
        i += 1


def enter_code(key) :
    global CURRENT_CODE
    
    CURRENT_CODE += key
    pprint('Code:\n{}'.format(CURRENT_CODE if SHOW_CODE else '*' * len(CURRENT_CODE)))
          
    if CURRENT_CODE == CORRECT_CODE :
        return update_state(STATE_VALID_CODE)
    
    elif len(CURRENT_CODE) >= len(CORRECT_CODE) :
        return update_state(STATE_INVALID_CODE)
    
    elif CURRENT_CODE in SPECIAL_CODES :
        update_state(SPECIAL_CODES[CURRENT_CODE])
        CURRENT_CODE = ""
        return


def enter_master_code(key) :
    global CURRENT_CODE
    
    CURRENT_CODE += key
    pprint('Code:\n{}'.format(CURRENT_CODE if SHOW_CODE else '*' * len(CURRENT_CODE)))
          
    if CURRENT_CODE == MASTER_CODE :
        return update_state(STATE_VALID_CODE)
    
    elif len(CURRENT_CODE) >= len(MASTER_CODE) :
        return update_state(STATE_INVALID_CODE)
    

def key_pressed(key) :
    global LAST_ACTION_AT, LCD_BACKLIGHT_STATE
    LAST_ACTION_AT = time.time()
    key = str(key)

    # On keypress, turn LCD backlight back on
    if LCD_BACKLIGHT != "off" and LCD_BACKLIGHT_STATE == False :
        display.lcd_backlight(True)
        LCD_BACKLIGHT_STATE = True

    # If we are on home or in enter code mode
    if CURRENT_STATE & (STATE_HOME | STATE_ENTER_CODE) :
        enter_code(key)
        return

    # If we are in master code mode
    if CURRENT_STATE & STATE_MASTER_CODE :
        enter_master_code(key)
        return


def main() :
    global display, servo, keypad, LCD_BACKLIGHT_STATE, CURRENT_CODE
    try:
        # Load the driver and set it to "display"
        display = drivers.Lcd()
        display.lcd_backlight(LCD_BACKLIGHT_STATE)

        pprint('Initialize...')

        # Start by initializing motor and put him back to max position (open)
        factory = PiGPIOFactory()
        servo = Servo("BOARD12", pin_factory = factory, min_pulse_width = 1/1000, max_pulse_width = 2.5/1000)
        servo.max()
        time.sleep(0.2)

        factory = rpi_gpio.KeypadFactory()
        keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

        keypad.registerKeyPressHandler(key_pressed)

        update_state(STATE_HOME)

        while True:
            # After 10 sec, stop lcd light to limit current consumption
            if LCD_BACKLIGHT == "auto" and LCD_BACKLIGHT_STATE and time.time() - LAST_ACTION_AT > 10 :
                display.lcd_backlight(False)
                LCD_BACKLIGHT_STATE = False

            if CURRENT_STATE == STATE_HOME and PREVIOUS_STATE != STATE_HOME :
                pprint("Waiting for code\n...")
                update_state(STATE_HOME) # Re-update to show message only one time
                time.sleep(0.5)
                continue

            if CURRENT_STATE == STATE_INVALID_CODE :
                pprint("Invalid code!")
                time.sleep(5)
                CURRENT_CODE = ""
                update_state(STATE_HOME)
                continue

            if CURRENT_STATE == STATE_VALID_CODE :
                pprint("Valid code.\nOpening safe.")
                # Opening safe for 1/2 sec then release so it close when user close the door
                servo.min()
                time.sleep(0.5)
                servo.max()
                time.sleep(0.5)
                CURRENT_CODE = ""
                update_state(STATE_HOME)
                continue

            if CURRENT_STATE == STATE_MASTER_CODE :
                if PREVIOUS_STATE != STATE_MASTER_CODE :
                    update_state(CURRENT_STATE) # Re-update to show message only one time
                    pprint('SUPER...')
                    time.sleep(0.5)
                    continue           

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Goodbye")

    finally:
        cleanup_keypad()
        display.lcd_backlight(False)
        display.lcd_clear()


if __name__ == "__main__" :
    main()
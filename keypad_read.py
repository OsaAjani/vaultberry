from pad4pi import rpi_gpio
from time import sleep
import RPi.GPIO as GPIO

KEYPAD = [
    [1, 2, 3, "A"],
    [4, 5, 6, "B"],
    [7, 8, 9, "C"],
    ["*", 0, "#", "D"]
]

ROW_PINS = [4, 17, 27, 22] # BCM numbering
COL_PINS = [23, 24, 25, 8] # BCM numbering

try :
    factory = rpi_gpio.KeypadFactory()

    # Try factory.create_4_by_3_keypad
    # and factory.create_4_by_4_keypad for reasonable defaults
    keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

    def printKey(key):
        print(key)

    # printKey will be called each time a keypad button is pressed
    #keypad.registerKeyPressHandler(printKey)

    key = False
    print('Read key : ')
    while not key :
        key = keypad.getKey()
        sleep(0.1)

    print("Key pressed : {}\n".format(key))
except Exception as e :
    print("Error : {}".format(e))
finally :
    keypad.cleanup()

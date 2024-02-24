#! /usr/bin/env python
import drivers
from time import sleep

# Load the driver and set it to "display"
# If you use something from the driver library use the "display." prefix first
display = drivers.Lcd()

# Main body of code
try:
    # Remember that your sentences can only be 16 characters long!
    print("Writing to display")
    display.lcd_display_string("Line 1!", 1)  # Write line of text to first line of display
    display.lcd_display_string("Press Ctrl+C!", 2)  # Write line of text to second line of display
    while True :
        sleep(2)
except KeyboardInterrupt:
    # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    display.lcd_clear()

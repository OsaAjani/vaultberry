from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

from time import sleep

factory = PiGPIOFactory()

servo = Servo("BOARD12", pin_factory = factory, min_pulse_width = 1/1000, max_pulse_width = 2.5/1000)
print("Go to min")
servo.min()
sleep(1)
servo.value = None;

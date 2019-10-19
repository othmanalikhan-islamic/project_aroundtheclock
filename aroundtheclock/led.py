"""
Responsible for controlling the Raspberry Pi pins connected to an LED.
"""


import RPi.GPIO as GPIO
import time


def initialisePi(pin: int):
    """
    Initialises the PIN to be connected to the LED.

    :param pin: The pin connected to the LED.
    :return: RPi.GPIO.PWM, representing the pin connected to the LED.
    """
    FREQUENCY = 1000

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.setup(pin, GPIO.LOW)

    led = GPIO.PWM(pin, FREQUENCY)
    led.start(0)
    return led


def blinkLED(pin, speed: int):
    """
    Causes the LED to gradually change brightness (0% -> 100% -> 0%).

    :param pin: RPi.GPIO.PWM, representing the pin connected to the LED.
    :param speed: The number of seconds the LED takes to blink fully.
    """
    INTERVAL = 1
    MIN_PERCENT = 0
    MAX_PERCENT = 100
    STEPS = (MAX_PERCENT - MIN_PERCENT) / INTERVAL
    DUTY_DELAY = speed / (2 * STEPS)

    for percentage in range(MIN_PERCENT, MAX_PERCENT, INTERVAL):
        pin.ChangeDutyCycle(percentage)
        time.sleep(DUTY_DELAY)

    for percentage in range(MAX_PERCENT, MIN_PERCENT, -INTERVAL):
        pin.ChangeDutyCycle(percentage)
        time.sleep(DUTY_DELAY)


def main():
    """
    Entry point of the module.
    """
    LED_PIN = 18
    led = initialisePi(LED_PIN)
    blinkLED(led, 3)


if __name__ == "__main__":
    main()


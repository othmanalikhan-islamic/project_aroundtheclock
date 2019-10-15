"""
Responsible for controlling the Raspberry Pi pins.
"""


import RPi.GPIO as GPIO
import time


LED_PIN = 18


def initialisePi():
    """
    Initialises the PIN to be connected to the LED.

    :return:
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.setup(LED_PIN, GPIO.LOW)

    led = GPIO.PWM(LED_PIN, 1000)
    led.start(0)
    return led


def blinkLED(pin, pause):
    """

    :param pin:
    :param pause: Integer, the number of seconds to
    :return:
    """
    DUTY_DELAY = 0.05

    print("Fire me up Scotty! (Pin 18)")

    for percentage in range(0, 100, 5):
        pin.ChangeDutyCycle(percentage)
        time.sleep(DUTY_DELAY)

    for percentage in range(100, 0, -5):
        pin.ChangeDutyCycle(percentage)
        time.sleep(DUTY_DELAY)

    print("Power is dry!")


def main():
    """
    Entry point of the module.
    """
    led = initialisePi()
    blinkLED(led, 1)


if __name__ == "__main__":
    main()

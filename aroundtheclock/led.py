"""
Responsible for controlling the Raspberry Pi pins connected to an LED.
"""


# import RPi.GPIO as GPIO
GPIO = None
import time


def initialisePi(pin: int):
    """
    Initialises the PIN to be connected to the LED.

    :param pin: The pin connected to the LED.
    :return:
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

    :param pin:
    :param speed: The number of seconds the LED takes to blink.
    """
    INTERVAL = 5
    MIN_PERCENT = 0
    MAX_PERCENT = 100
    STEPS = (MAX_PERCENT - MIN_PERCENT) / INTERVAL
    DUTY_DELAY = speed / (2 * STEPS)

    print(f"Fire me up Scotty! (Pin {pin})")

    for percentage in range(0, 100, 5):
        pin.ChangeDutyCycle(percentage)
        time.sleep(DUTY_DELAY)

    for percentage in range(100, 0, -5):
        pin.ChangeDutyCycle(percentage)
        time.sleep(DUTY_DELAY)

    print("Power's dry!")


def main():
    """
    Entry point of the module.
    """
    LED_PIN = 18
    led = initialisePi(LED_PIN)
    blinkLED(led, 1)


if __name__ == "__main__":
    main()


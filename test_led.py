import time
import configparser
import RPi.GPIO as GPIO #Used to interface with hardware on the Raspberry Pi.

#
# load config file
#
config = configparser.ConfigParser()
config.read('config.ini')

LED = [config.getint('receiver', 'pin_red'), config.getint('receiver', 'pin_amber'), config.getint('receiver', 'pin_green')]

#Define some values to use later in the script.
RED, AMBER, GREEN = 0, 1, 2

def gpio_setup():
    """
    Use GPIO.BOARD so we can call the pins by their physical position in P1.
    Set each of the pins as outputs.
    """
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    for led in (RED, AMBER, GREEN):
        GPIO.setup(LED[led],GPIO.OUT)


def control_lights(state):
    """
    Control the Pi-Stop LEDs by setting them to the required
    states (and wait).
    i.e. TRUE=ON FALSE=OFF
    """
    for led in (RED, AMBER, GREEN):
        GPIO.output(LED[led],state[led])


if __name__ == '__main__':     # Program start from here
    gpio_setup()

    while True:
        control_lights((True, False, False))
        time.sleep(1)
        control_lights((True, True, False))
        time.sleep(1)
        control_lights((True, True, True))
        time.sleep(1)
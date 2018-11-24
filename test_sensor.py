import configparser
import json
import platform, sys
import VL53L0X
import RPi.GPIO as GPIO #Used to interface with hardware on the Raspberry Pi.
from time import sleep

config = configparser.ConfigParser()
config.read('config.ini')

RED, AMBER, GREEN = 0, 1, 2
LED = [config.getint('receiver', 'pin_red'), config.getint('receiver', 'pin_amber'), config.getint('receiver', 'pin_green')]
state = (1, 1, 1)

def gpio_setup():
    """
    Use GPIO.BOARD so we can call the pins by their physical position in P1.
    Set each of the pins as outputs.
    """
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    for led in (RED, AMBER, GREEN):
        GPIO.setup(LED[led], GPIO.OUT)


def control_lights(state):
    """
    Control the Pi-Stop LEDs by setting them to the required
    states (and wait).
    i.e. TRUE=ON FALSE=OFF
    """
    for led in (RED, AMBER, GREEN):
        GPIO.output(LED[led], state[led])


if __name__ == '__main__':     # Program start from here
    gpio_setup()

    tof = VL53L0X.VL53L0X()
    tof.open()

    # Start ranging
    tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)

    timing = tof.get_timing()

    if (timing < 20000):
        timing = 20000

    while True:
        distance = tof.get_distance()
        print (distance)

        if 0 <= distance <= 200:
            state = (1,0,0)
        elif 200 <= distance <= 500:
            state = (0, 1, 0)
        else:
            state = (0, 0, 1)

        control_lights(state)

        sleep(0.1)

    tof.stop_ranging()
    tof.close()

import configparser
import json
import platform, sys
import logging
import pysher
import RPi.GPIO as GPIO #Used to interface with hardware on the Raspberry Pi.
from time import sleep

IS_RASPBERRY_PI = 'arm' in platform.platform()

#
# load config file
#
config = configparser.ConfigParser()
config.read('config.ini')

DEBUG = config.getboolean('general', 'debug')
CONTROL_RANGE_START = config.getint('receiver', 'control_range_start')
CONTROL_RANGE_END = config.getint('receiver', 'control_range_end')

LED = [config.getint('receiver', 'pin_red'), config.getint('receiver', 'pin_amber'), config.getint('receiver', 'pin_green')]
RED, AMBER, GREEN = 0, 1, 2

#
# setup logging
#
#logger = logging.getLogger(__name__)
#logger.setLevel("DEBUG")

#if DEBUG:
#    h = logging.StreamHandler(sys.stdout)
#else:
#    h = logging.FileHandler('log.txt')

#h.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
#logger.addHandler(h)

last_distance = 0
show_lights = True
state = (1, 1, 1)
status = ""

#sys.stdout = open('log.txt', 'a')

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
    global show_lights

    if show_lights:
        for led in (RED, AMBER, GREEN):
            GPIO.output(LED[led], state[led])
    else:
        for led in (RED, AMBER, GREEN):
            GPIO.output(LED[led], 0)


def status_changed_func(data):
    global status, state, show_lights

    """ when status changed, this function will be called from pusher"""

    result = json.loads(data)

    new_status = result['status'].upper()

    if new_status != status:
        status = new_status
        
        if status == 'OCCUPIED':
            logger.log(logging.DEBUG, 'occupied, now show show red light')
            if show_lights:
                # now show amber
                state = (0, 1, 0)
                control_lights(state)

                sleep(2)

                # now show red
                state = (1, 0, 0)
                control_lights(state)                    

        else:
            logger.log(logging.DEBUG, 'Free, now show show green light')

            if show_lights:
                # now show red amber light
                state = (1, 1, 0)
                control_lights(state)

                sleep(2)

                # now show green
                state = (0, 0, 1)
                control_lights(state)


if __name__ == '__main__':     # Program start from here
    #
    # receiver
    #

#    pusher.connection.bind('pusher:connection_established', connect_handler)
#    pusher.connect()

    if IS_RASPBERRY_PI:
        import VL53L0X
        gpio_setup()

 #       control_lights(state)
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
#
#            if DEBUG:
#                logger.log(logging.DEBUG, 'Distance: {}'.format(distance))
            # print (timing/1000000)

            # if DEBUG:
            #     print ("Distance: {}".format(distance))
            if 0 <= distance <= 200:
                state = (1,0,0)
            elif 200 <= distance <= 400:
                state = (0, 1, 0)
            else:
                state = (0, 0, 1)

#                if last_distance > CONTROL_RANGE_END:
#                    show_lights = not show_lights
            control_lights(state)

 #           last_distance = distance

            sleep(0.1)

        tof.stop_ranging()
        tof.close()

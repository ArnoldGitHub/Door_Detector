import configparser
import platform, sys
import logging
from pusher import Pusher
from time import sleep

IS_RASPBERRY_PI = 'arm' in platform.platform()

if IS_RASPBERRY_PI:
    import VL53L0X
    import RPi.GPIO as GPIO

#
# load config file
#
config = configparser.ConfigParser()
config.read('config.ini')

DEBUG = config.getboolean('general', 'debug')
OCCUPIED_RANGE_START = config.getint('sender', 'occupied_range_start')
OCCUPIED_RANGE_END = config.getint('sender', 'occupied_range_end')

LED = [config.getint('sender', 'pin_red'), config.getint('sender', 'pin_amber'), config.getint('sender', 'pin_green')]
RED, AMBER, GREEN = 0, 1, 2

#
# setup logging
#
logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

if DEBUG:
    h = logging.StreamHandler(sys.stdout)
else:
    h = logging.FileHandler('log.txt')

h.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
logger.addHandler(h)

status = ''
state = (1, 1, 1)
pusher = object()

def set_status(_status):
    global status, pusher, config, DEBUG

    if not status == _status:
        logger.log(logging.DEBUG, 'sender set {}'.format(_status))

        status = _status

        if status.upper() == 'OCCUPIED':
            # now show amber
            state = (0, 1, 0)
            control_lights(state)

            sleep(2)

            # now show red
            state = (1, 0, 0)
            control_lights(state)
        elif status.upper() == 'FREE':
            # show red amber light
            state = (1, 1, 0)
            control_lights(state)

            sleep(2)

            # now show green
            state = (0, 0, 1)
            control_lights(state)

        #
        # notify pusher
        #
        pusher_channel = config.get('pusher', 'channel')
        pusher.trigger(pusher_channel, 'status_changed', {'status': status})


def gpio_setup():
    """
    Use GPIO.BOARD so we can call the pins by their physical position in P1.
    Set each of the pins as outputs.
    """
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    #
    # LED setup
    #
    for led in (RED, AMBER, GREEN):
        GPIO.setup(LED[led], GPIO.OUT)


def control_lights(state):
    """
    Control the Pi-Stop LEDs by setting them to the required
    states (and wait).
    i.e. TRUE=ON FALSE=OFF
    show lights only if the button is ok
    """
    try:
        for led in (RED, AMBER, GREEN):
            GPIO.output(LED[led], state[led])
    except:
        pass


if __name__ == '__main__':     # Program start from here
    pusher = Pusher(
        app_id=config.get('pusher', 'app_id'),
        key=config.get('pusher', 'key'),
        secret=config.get('pusher', 'secret'),
        cluster=config.get('pusher', 'cluster'),
        ssl=True
    )

    if IS_RASPBERRY_PI:
        gpio_setup()

        tof = VL53L0X.VL53L0X()

        # Start ranging
        tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)

        timing = tof.get_timing()
        if (timing < 20000):
            timing = 20000

        while True:
            distance = tof.get_distance()

            if OCCUPIED_RANGE_START <= distance <= OCCUPIED_RANGE_END:
                set_status('OCCUPIED')
            else:
                set_status('FREE')

            sleep(0.2)

        tof.stop_ranging()
import RPi.GPIO as GPIO
import os
import json
import logging.config

# HIGH == OFF, LOW == ON
OFF=GPIO.HIGH
ON=GPIO.LOW

# Logging setup
def setup_logging(
    default_path='logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

setup_logging()
#logger = logging.getLogger(__name__)
logger = logging.getLogger('fandev')

### CONFIG BEGIN ###
# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
    17 : {'name' : 'LIGHT',    'state' : OFF},
    18 : {'name' : 'FAN_OFF',  'state' : OFF},
    27 : {'name' : 'FAN_LOW',  'state' : OFF},
    22 : {'name' : 'FAN_MED',  'state' : OFF},
    23 : {'name' : 'FAN_HIGH', 'state' : OFF}
}

ipaddr='0.0.0.0'
port = 8080
database = "fan.db"
debug=False

### CONFIG END ###


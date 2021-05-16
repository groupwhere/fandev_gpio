import RPi.GPIO as GPIO
import os
import json
import logging.config

# HIGH == OFF, LOW == ON
OFF=GPIO.HIGH
ON=GPIO.LOW
#BOUNCE = 2000

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

# default admin passwd is fanpass
# This must be processed with md5 if you wish to change it.
users = {
    'admin': '182c22637d8049ff3327e161ed614f28'
}
ipaddr='0.0.0.0'
port = 8080
database = "fan.db"
debug=True
### CONFIG END ###


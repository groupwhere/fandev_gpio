import RPi.GPIO as GPIO

# HIGH == OFF, LOW == ON
OFF=GPIO.HIGH
ON=GPIO.LOW

### CONFIG BEGIN ###
# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
    17 : {'name' : 'LIGHT',    'state' : OFF},
    18 : {'name' : 'FAN_OFF',  'state' : OFF},
    27 : {'name' : 'FAN_LOW',  'state' : OFF},
    22 : {'name' : 'FAN_MED',  'state' : OFF},
    23 : {'name' : 'FAN_HIGH', 'state' : OFF}
}

port = 8080
database = "fan.db"
debug=False
### CONFIG END ###

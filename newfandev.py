import sqlite3
import inspect
from time import sleep
import RPi.GPIO as GPIO

from config import *
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Active low
# HIGH == OFF, LOW == ON
OFF=GPIO.HIGH
ON=GPIO.LOW

# This version, in newfandev.py, sets the GPIO pins as inputs when the app is not
# Setting output values.  When changing outputs, the pins are set as outputs.
#
# This is a work in progress and is being done to monitor
# and update from local keypresses at the remote.
#
# See this for perhaps a better alternative
# http://raspberry.io/projects/view/reading-and-writing-from-gpio-ports-from-python/
class FanDev():
    def __init__(self, database=None, newpins=False, debug=False):
        self.database = database
        self.debug = debug

        self.cbset = False

        if newpins:
            self.pins = newpins
        else:
            #self.pins = {}
            self.pins = pins

        self.nametopin = {}
        self.pininit(True)

        if self.database:
            self.readdb(newpins)

        self.fanset('OFF')

    # Initialize GPIO as output with callback for inputs
    def pininit(self,startup=False):
        if self.debug:
            logger.info("pininit() called")
            logger.info("caller name: " + inspect.stack()[1][3])

        for pin in self.pins:
            if self.debug:
                logger.info("setting up GPIO " + str(pin) + " as output")

            if self.cbset == False:
                GPIO.setup(pin, GPIO.IN)
                GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.pinread, bouncetime=2000)
                #GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.pinread, bouncetime=int(BOUNCE))

            GPIO.setup(pin, GPIO.OUT)
            if startup == True:
                GPIO.output(pin, OFF)

        self.cbset = True

    def pinread(self, channel):
        if self.debug:
            logger.info("pinread(" + str(channel) + ")")

        if self.pins[channel]['state'] == ON:
            self.pins[channel]['state'] = OFF
        else:
            self.pins[channel]['state'] = ON

        self.writedb()

    # Cycle the light pin
    def lightsw(self):
        for pin, data in self.pins.iteritems():
            if 'LIGHT' in data['name']:
                logger.info("lightsw()");
                self.fire_gpio(pin)

    # Set fan to OFF, LOW, MED, or HIGH
    def fanset(self, status='OFF'):
        if self.debug:
            logger.info("fanset(" + str(status) + ")")
            logger.info("caller name: " + inspect.stack()[1][3])

        # Ensure uppercase to match pin names
        action = 'FAN_' + status.upper()

        # Set all the fan pins off
        for pin, data in self.pins.iteritems():
            if 'FAN' in data['name']:
                self.set_gpio(pin, OFF)

        # Now cycle on the pin we want
        self.fire_gpio(self.nametopin[action])

    # Set a pin on or OFF
    def set_gpio(self, changePin, setting):
        #self.pininit()
        if self.debug:
            logger.info("set_gpio(" + str(changePin) + "," + str(setting) + ")")
            logger.info("caller name: " + inspect.stack()[1][3])

        GPIO.output(changePin, setting)

        self.pins[changePin]['state'] = setting
        self.writedb()
        #self.pinread()

    # Cycle a pin on then off again
    def fire_gpio(self, changePin):
        #self.pininit()
        if self.debug:
            logger.info("fire_gpio(" + str(changePin) + ")")
            logger.info("caller name: " + inspect.stack()[1][3])

        # We only need about 1/4 a second to cycle the chosen pin low and then back to high
        GPIO.output(changePin, ON)
        sleep(0.25)
        GPIO.output(changePin, OFF)

        if self.pins[changePin]['state'] == ON:
            self.pins[changePin]['state'] = OFF
        else:
            self.pins[changePin]['state'] = ON
        self.writedb()
        #self.pinread()

    def checkstate(self):
        logger.info(str(self.pins))
        logger.info(str(self.nametopin))

    def getpins(self):
        for pin in self.pins:
            self.pins[pin]['state'] = GPIO.input(pin)
        self.writedb()

    def readdb(self, newpins=False):
        if self.debug:
            logger.info("readdb(" + str(newpins) + ")")
            logger.info("caller name: " + inspect.stack()[1][3])

        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        # Verify that the table exists
        c.execute('CREATE TABLE IF NOT EXISTS pins (pin INT, name TEXT, state BOOL)')
        conn.commit()

        if newpins:
            c.execute('DELETE FROM pins')
            conn.commit()
            row = 0
        else:
            # Check for existing records
            c.execute('SELECT COUNT(pin) FROM pins')
            row = c.fetchone()[0]

        if row == 0:
            # No records, insert values from pins table
            if self.debug:
                logger.error("NO ROWS!!!")

            for pin in self.pins:
                c.execute('INSERT INTO pins VALUES (?, ?, ?)', (int(pin), self.pins[pin]['name'], bool(self.pins[pin]['state'])))
                if self.debug:
                    logger.info("inserting row...")
                conn.commit()

        # Read the table
        for row in c.execute('SELECT * FROM pins'):
            if self.debug:
                logger.info("Reading row...")
            self.pins[int(row[0])] = {'name': row[1], 'state': row[2]}
            self.nametopin[row[1]] = int(row[0])

        conn.close()

    def writedb(self):
        # Update the existing table rows
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        if self.debug:
            logger.info("writedb() called")
            logger.info(str(self.pins))

        for pin in self.pins:
            c.execute("UPDATE pins SET state=? WHERE pin=?", (bool(self.pins[pin]['state']), int(pin)))
            if self.debug:
                logger.info("updating row...")
            conn.commit()

# If you send pins, it will clear the db and install the new pins
#fan = FanDev(database, pins, debug)
# Otherwise, it will read the database for the current info
#fan = FanDev(database, False, debug)
#fan.checkstate()

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

class FanDev():
    def __init__(self, database=None, newpins=False, debug=False):
        self.database = database
        self.debug = debug

        if newpins:
            self.pins = newpins
        else:
            #self.pins = {}
            self.pins = pins

        self.nametopin = {}

        if self.database:
            self.readdb(newpins)

        self.pininit()
        self.fanset('OFF')

    # Cycle the light pin
    def lightsw(self):
        for pin, data in self.pins.iteritems():
            if 'LIGHT' in data['name']:
                self.fire_gpio(pin)

    # Set fan to OFF, LOW, MED, or HIGH
    def fanset(self, status='OFF'):
        if self.debug:
            print "fanset(", status, ")"
            print 'caller name:', inspect.stack()[1][3]

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
        if self.debug:
            print "set_gpio(", changePin, ",", setting, ")"
            print 'caller name:', inspect.stack()[1][3]
        GPIO.output(changePin, setting)

        self.pins[changePin]['state'] = setting
        self.writedb()

    # Cycle a pin on then off again
    def fire_gpio(self, changePin):
        if self.debug:
            print "fire_gpio(", changePin, ")"
            print 'caller name:', inspect.stack()[1][3]
        # We only need about 1/4 a second to cycle the chosen pin low and then back to high
        GPIO.output(changePin, ON)
        sleep(0.25)
        GPIO.output(changePin, OFF)

        if self.pins[changePin]['state'] == ON:
            self.pins[changePin]['state'] = OFF
        else:
            self.pins[changePin]['state'] = ON
        self.writedb()

    def checkstate(self):
        print self.pins
        print self.nametopin

    # Initialize GPIO (pin init)
    def pininit(self):
        if self.debug:
            print "pininit() called"
        for pin in self.pins:
            #print(pin)
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, OFF)

    def getpins(self):
        for pin in self.pins:
            self.pins[pin]['state'] = GPIO.input(pin)
        self.writedb()

    def readdb(self, newpins=False):
        if self.debug:
            print 'readdb(' + str(newpins) + ')'
            print 'caller name:', inspect.stack()[1][3]

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
                print "NO ROWS!!!"

            for pin in self.pins:
                c.execute('INSERT INTO pins VALUES (?, ?, ?)', (int(pin), self.pins[pin]['name'], bool(self.pins[pin]['state'])))
                if self.debug:
                    print "inserting row..."
                conn.commit()

        # Read the table
        for row in c.execute('SELECT * FROM pins'):
            if self.debug:
                print "Reading row..."
            self.pins[int(row[0])] = {'name': row[1], 'state': row[2]}
            self.nametopin[row[1]] = int(row[0])

        conn.close()

    def writedb(self):
        # Update the existing table rows
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        if self.debug:
            print self.pins
        for pin in self.pins:
            c.execute("UPDATE pins SET state=? WHERE pin=?", (bool(self.pins[pin]['state']), int(pin)))
            if self.debug:
                print "updating row..."
            conn.commit()

# If you send pins, it will clear the db and install the new pins
#fan = FanDev(database, pins, debug)
# Otherwise, it will read the database for the current info
#fan = FanDev(database, False, debug)
#fan.checkstate()

import RPi.GPIO as GPIO
#import sqlite3
import datetime
from flask import Flask, render_template, request
from flask_restful import Resource, Api
from webargs import fields, validate
from webargs.flaskparser import use_kwargs, parser
import json

app = Flask(__name__)
api = Api(app)

from config import *
from fandev import FanDev
#from newfandev import FanDev

# Create a fan device
# Use this line to init from the pins var in config.py.  Note that on the first run,
#   the database will automatically be initialized from the pins var.
#   So, use this only if you have to make changes to the pin config, and only once.
#fan = FanDev(database, pins, debug)
fan = FanDev(database, False, debug)

# Following routes are for users with a browser.  Below that are API calls using JSON
@app.route("/", methods = ['GET', 'POST'])
def main():
    try:
        data = request.form
        logger.info("Received: %s", data)
        if data['light'] != None:
            fan.lightsw()
    except:
        logger.info("No light change received")

    try:
        if data['fanstate'] != None:
            fan.fanset(data['fanstate'])
    except:
        logger.info("No fan change received")

    # Pass the template data into the template main.html and return it to the user
    light = fan.nametopin['LIGHT']

    off_sel = low_sel = med_sel = high_sel = ''
    for pin in fan.pins:
        if 'OFF' in fan.pins[pin]['name'] and fan.pins[pin]['state'] == ON:
            off_sel = 'checked'
        elif 'LOW' in fan.pins[pin]['name'] and fan.pins[pin]['state'] == ON:
            low_sel = 'checked'
        elif 'MED' in fan.pins[pin]['name'] and fan.pins[pin]['state'] == ON:
            med_sel = 'checked'
        elif 'HIGH' in fan.pins[pin]['name'] and fan.pins[pin]['state'] == ON:
            high_sel = 'checked'
        else:
            off_sel = 'checked'

    logger.info("PINS: %s", fan.pins)

    # Put the pin dictionary into the template data dictionary:
    templateData = {
        'pins'    : fan.pins,
        'light'   : light,
        'off_sel' : off_sel,
        'low_sel' : low_sel,
        'med_sel' : med_sel,
        'high_sel': high_sel,
    }

    return render_template('main.html', **templateData)

# API calls via json
class FanApi(Resource):
    args = {
        'LIGHT': fields.Str(),
        'FAN_OFF': fields.Str(),
        'FAN_LOW': fields.Str(),
        'FAN_MED': fields.Str(),
        'FAN_HIGH': fields.Str()
    }

    def get(self):
        data = json.dumps(pins)
        return data

    @use_kwargs(args)
    def put(self, LIGHT, FAN_HIGH, FAN_MED, FAN_LOW, FAN_OFF):
        if LIGHT:
            fan.lightsw()
        if FAN_HIGH:
            fan.fanset('HIGH')
        elif FAN_MED:
            fan.fanset('MED')
        elif FAN_LOW:
            fan.fanset('LOW')
        elif FAN_OFF:
            fan.fanset('OFF')

        data = json.dumps(fan.pins)
        return data

api.add_resource(FanApi, '/api')

if __name__ == "__main__":
    app.run(host=ipaddr, port=port, debug=True, use_reloader=False)

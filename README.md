# fandev_gpio
Control a 5 switch ceiling fan remote using pi zero

This was inspired by the desire to automate a ten year old ceiling fan with an RF remote.  Rather than replace the whole thing, or engineer an RF solution on my own, I opted to hack into the remote.

The remote is a 5-button device with switches for Light on/off and Fan off/low/medium/high:

![fan remote](https://github.com/groupwhere/fandev_gpio/blob/master/fanremote.jpg)

Findings:
```
1. The remote uses an HT12E encoder chip with a matching HT12D decoder in the fan base.
2. The remote uses a 9V battery.  But, the device will work with a drained battery as low as
	2.4V per the datasheet.  A Pi/PiZero 5V supply is more than adequate.
3. A PiZero will fit inside the remote with some modifications.  However, I am still working
	out issues possibly due to proximity but perhaps coding issues at the time.
4. The fan restores light status across power loss but not fan.  So, if the light and fan
	are on and you lose power, only the light will turn back on when power is restored.
5. There is no true feedback short of possibly adding a light sensor to the device.
```

More details to come on the connections.  But, now for the code:

This code includes a fandev.py which is the actual control point.  app.py is the web and api interface.  You only need to run app.py as root, or as another user with access to open a socket.  If using a port above 1024, this should not be an issue.

I elected to have the code turn the fan off on startup just to be sure of maintaining status of the fan.
Fandev.py uses a sqlite database to TRY to maintain status across power loss.  The only issue should be the light but it is possible to lose sync on the fan status as well.

It uses 5 GPIO pins, in my case GPIO 17, 18, 22, 23, and 27.  Fortunately, connecting these directly to the pads on the remote board worked well.

fandev cycles pins low and back to high by default with a sleep time of 1/4 second.  This simulates a human operating the remote and is enough time to trigger the functions.

Control:
You can access the web interface at http://your.dev.ice.ip:port/
From there you can switch the light on and off or set the fan to off/low/med/high.
This is a very primitive interface.  Beautification was not my goal but I welcome submissions ;)

There is also an api using flask_restful.  If you access http://your.dev.ice.ip:port/api, it should return the following:

"{"17": {"state": 1, "name": "LIGHT"}, "18": {"state": 0, "name": "FAN_OFF"}, "27": {"state": 1, "name": "FAN_LOW"}, "22": {"state": 1, "name": "FAN_MED"}, "23": {"state": 1, "name": "FAN_HIGH"}}"

This shows the state of all switches.  Note that this is not the actual pin state since we only toggle the pins low as needed.  But, the return value should show which condition was last set and recalled from the database.

To set the light on, you can post as follows:

curl -H "Content-Type: application/json" -X PUT -d '{"LIGHT":"on"}' http://your.dev.ice.ip:port/api

```json
{
    "17": {
        "name": "LIGHT",
        "state": 0
    },
    "18": {
        "name": "FAN_OFF",
        "state": 0
    },
    "22": {
        "name": "FAN_MED",
        "state": 1
    },
    "23": {
        "name": "FAN_HIGH",
        "state": 1
    },
    "27": {
        "name": "FAN_LOW",
        "state": 1
    }
}
```

It doesn't matter whether you send on or off, etc.  We will toggle the condition of the light when you send anything.

To set the fan to low, post as follows:

curl -H "Content-Type: application/json" -X PUT -d '{"FAN_LOW":"on"}' http://your.dev.ice.ip:port/api

```json
{
    "17": {
        "name": "LIGHT",
        "state": 1
    },
    "18": {
        "name": "FAN_OFF",
        "state": 1
    },
    "22": {
        "name": "FAN_MED",
        "state": 1
    },
    "23": {
        "name": "FAN_HIGH",
        "state": 1
    },
    "27": {
        "name": "FAN_LOW",
        "state": 0
    }
}
```

Since we work with active lows, matching the remote circuit, 0 means the switch was activated.


There is also newfandev.py.  This is a work in progress to set the pins back to inputs to monitor
local keypresses at the remote, since it is still connected.

Similar project:
https://community.home-assistant.io/t/rf-ceiling-fan-remote-hack/42304

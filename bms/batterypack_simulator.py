# Author: Arun Santhanagopalan

# Description : This is the simulator module mimicking actual battery pack in a evTOL


import pandas as pd
import datetime
import pickledb
db = pickledb.load('batterystate.db', False)

db.set('fullcapacity', 100)


def init_batterypack(n):

    db.set("batterypacks", n)
    for i in range(1, n):
        db.set('battery'+str(i),db.get('fullcapacity')/n)
    db.set("remaining_capacity", db.get('fullcapacity'))
    return f"Battery Pack of {n} Intialized with Capacity {db.get('fullcapacity')}"


def allocate_power(power):

    # batteryPack['capacity'] = batteryPack['capacity'] - (power/len(batteryPack))
    for i in range(1, db.get("batterypacks")):
        db.set('battery' + str(i), db.get('battery' + str(i)) - (power / db.get("batterypacks")))
    db.set("remaining_capacity",db.get('remaining_capacity') - power)

    return '{"remaining":' + str((db.get("remaining_capacity")/db.get("fullcapacity"))) + '}'

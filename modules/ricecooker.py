import json
import time
from datetime import datetime
import os


class RiceCooker:
    """ Rice Cooker Monitor  """
    # maximum time allowed in seconds
    MAXTIMEON = 7200
    # POWERON is in watts, draws about 50wts in heating mode 400wts running
    POWERON = 10
    def __init__(self, name):
        self.telemetry = 'tele/ricecooker/SENSOR'
        self.name = name
        self.payload = None
    
    def run(self, client, top):
        startTime = None
        while True:
            payload = self.payload.get()[self.telemetry]
            currentTime = datetime.now()          
            try:
                if (payload['ENERGY']['Power'] > self.POWERON):
                    if (startTime is None):
                        startTime = currentTime
                    runTime = (currentTime - startTime).total_seconds()
                    if (runTime > self.MAXTIMEON):
                        client.publish("cmnd/ricecooker/POWER", "OFF")
                        msg = "Shutting Rice Cooker down"
                        client.publish("stat/house/MESSAGES", json.dumps({"Location" : "Kitchen", "Time": currentTime.isoformat(), "Message" : msg, "Alert": "alert3"}))
                        startTime = currentTime
                else:
                    startTime = None
            except KeyError:
                continue
        





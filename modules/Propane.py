import json
import time
from datetime import datetime
import os
from fluids.geometry import TANK


class Propane:
    PUBTOPIC = "tele/Propane/LEVEL"
    TANKDIAMETER = 37
    TANKLENGTH = (120 - TANKDIAMETER)
    TANKCAPRADIUS = (TANKDIAMETER / 2)

    """ Mopeka Propane Level Monitor  """
    def __init__(self, name):
        self.telemetry = ['tele/Propane/SENSOR', 'tele/Propane/STATE']
        self.name = name
        self.payload = None
        self.tank = TANK(D = self.TANKDIAMETER, L = self.TANKLENGTH, horizontal = True, sideA = "spherical", sideB = "spherical", sideA_a = self.TANKCAPRADIUS, sideB_a = self.TANKCAPRADIUS)
        # convert cubic inches to gallons
        self.tankVolume = self.tank.V_total / 231.0
    def run(self, client, top):
        online = 0
        while True:
            payloadList = self.payload.get()          
            try:
                if (self.telemetry[1] in payloadList):
                    online = 1 if (payloadList[self.telemetry[1]]['Connection'] == "ONLINE") else 0
                if (self.telemetry[0] in payloadList):
                    payload = payloadList[self.telemetry[0]]
                    height = payload['Tank']['Level']
                    # convert height to inches from mm, convert volume from in^3 to gallons
                    fuelRemaining = self.tank.V_from_h(height / 25.4)/ 231.0
                    fuelPercentage = round((fuelRemaining/self.tankVolume) * 100.0, 1)
                    fuelRemaining = round(fuelRemaining, 1)
                    client.publish(topic=self.PUBTOPIC,payload=json.dumps({"FuelPercentage" : fuelPercentage, "FuelRemaining": fuelRemaining, "Online" : online}), retain=False)
            except KeyError:
                continue





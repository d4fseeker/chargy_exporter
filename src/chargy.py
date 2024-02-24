import logging
from datetime import timedelta,datetime
import requests
from bs4 import BeautifulSoup
import json

##
## Chargy KML Handler
##
class ChargyData:

    #Default refresh interval
    EXPIRE_INTERVAL=timedelta(minutes=5)

    def __init__(self,url):
        self.url = url
        self.stations = None
        self.last_reloaded=None
        self.reload()

    def reload(self,expired_only=True):

        #If expired_only mode, only refresh if needed
        if expired_only and self.last_reloaded:
            if  ( datetime.now() - self.last_reloaded ) < self.EXPIRE_INTERVAL:
                return False
        
        #Reset variables
        self.stations = []
        self.last_reloaded = datetime.now()

        ##Get file
        logging.warn("Downloading new KML from Chargy: %s",self.url)
        resp = requests.get(self.url)
        xml = resp.text

        #logging.debug("READING LOCAL FILE FROM /TMP INSTEAD OF DOWNLOADING")
        #with open("/tmp/data.kml") as f:
        #    xml = f.read()

        #Parse XML
        self.data = BeautifulSoup(xml, "xml")

        #Iterate through places
        for entry in self.data.findAll("Placemark"):
            station = ChargerStation.load(entry)
            self.stations.append(station)

    #Print-ability
    def __str__(self):
        #Just return current stations array
        return str(self.stations)
    def __repr__(self):
        return self.__str__()


class ChargerStation:
    
    #BeautifulSoup KML Loader
    @classmethod 
    def load(cls,data):
        #Get name and create instance
        name = data.find("name").text.strip()
        instance = cls(name=name)

        #Add chargers
        for chargerdata in data.findAll("Data", {"name" : "chargingdevice"}):
            device = ChargerDevice.load(chargerdata)
            instance.addDevice(device)
        return instance

    #Contructor
    def __init__(self,name):
        self.name = name
        self.devices = []

    #Add charger
    def addDevice(self,device):
        self.devices.append(device)

    #Print-ability
    def __str__(self):
        return "Station<{}>{}".format(self.name,str(self.devices))
    def __repr__(self):
        return self.__str__()

class ChargerDevice:

    #BeautifulSoup KML Loader
    @classmethod
    def load(cls,data):
        #Get JSON
        jsondata = json.loads( data.find("value").text )

        #Create instance and add connectors
        instance = cls(id=jsondata["id"],name=jsondata["name"])
        for entry in jsondata["connectors"]:
            connector = ChargerConnector.load(entry)
            instance.addConnector(connector)

        return instance

    #Constructor
    def __init__(self,id,name):
        self.id = id
        self.name = name
        self.connectors = []

    #ADDer for charger connectors
    def addConnector(self,connector):
        self.connectors.append(connector)
    
    #COUNTer for connectors
    def countConnectors(self):
        return len(self.connectors)

    #Print-ability
    def __str__(self):
        return "Device<{}>{}".format(self.name,str(self.connectors))
    def __repr__(self):
        return self.__str__()

class ChargerConnector:

    #Enforce strict state handling: Throws ExceptionChargerConnectorInvalidState if state is unknown
    #Otherwise sets state to self.UNKNOWN_STATE
    STRICT_STATES=False

    UNKNOWN_STATE = "unavailable"       #Just assume a session state when we don't know what's happening

    #Simplified states
    STATE_CHARGING="charging"
    STATE_AVAILABLE="available"
    STATE_UNAVAILABLE="unavailable"

    STATES=[STATE_CHARGING,STATE_AVAILABLE,STATE_UNAVAILABLE]

    MAP_STATES={
        "CHARGING": "charging",         #Station is currently busy
        "AVAILABLE": "available",       #Station is ready for charging
        "UNAVAILABLE": "unavailable",   #Station is down for maintenance
        "OFFLINE": "unavailable",       #Station is not heartbeating
        "FAULT": "unavailable",         #Station is faulty
        "SUSPENDED_EV": "charging",     #Charging suspended by car
        "SUSPENDED_EVSE": "charging",   #Charging suspended by station
        "FINISHING": "charging",        #Charging session is terminating
        "PREPARING": "charging",        #Charging session is being setup
    }

    


    #JSON KML Loader
    @classmethod
    def load(cls,data):
        return cls(id=data["id"],name=data["name"],state=data["description"],speed=int(data["maxchspeed"]))


    #Constructor
    def __init__(self,id,name,state,speed):
        self.id = id
        self.name = name
        self.speed = int(speed)

        #Map state
        if state not in self.MAP_STATES:
            if self.STRICT_STATES:
                raise ExceptionChargerConnectorInvalidState("Unknown ChargerConnector state: {}".format(self.state))
            else:
                state = self.UNKNOWN_STATE
                logging.error("Unknown ChargerConnector state: %s",self.state)
        
        #Store state
        self.state = self.MAP_STATES[state]
        self.state_detailed = state
    
    #Print-ability
    def __str__(self):
        return "Connector<{}>".format(self.name)
    def __repr__(self):
        return self.__str__()
        

##
## Helper Classes
##

class ExceptionChargerConnectorInvalidState(ValueError):
    pass

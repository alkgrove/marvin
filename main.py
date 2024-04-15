
import os
import sys
import stat
import inspect
import traceback
import importlib
import mariadb
import queue as q
modulepath = os.path.abspath('./modules/')
sys.path.append(modulepath)
import configparser
import threading
from datetime import datetime
from multiprocessing import Process

import json
import paho.mqtt.client as mqtt

from daemonize import Daemonize
sys.path.append(os.path.abspath('./modules/'))

def classList(modulename):
    classes = inspect.getmembers(sys.modules[modulename], lambda member: inspect.isclass(member) and member.__module__ == modulename)
    return classes

webpath = "/var/www/html/marvin"
pid = "/run/marvin.pid"
candidates = ['/etc/marvin.conf', '/usr/local/etc/marvin.conf']

def on_connect(client, userdata, flags, rc):
    if (rc > 0):
        sys.exit("Connection failed: " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for topic in userdata:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    # payload is a dict object, msg payload is a string
    payload = dict()
    if (len(msg.payload) == 0):
        payload[msg.topic] = None
    else:
        try:
            payload[msg.topic] = json.loads(msg.payload)
        except ValueError:
            try:
                payload[msg.topic] = msg.payload.decode()
            except:
                payload[msg.topic] = "Unknown Payload"

    # set the queue for this payload
    if (msg.topic in userdata):
        for instance in userdata[msg.topic]['instance']:
            instance.payload.put(payload)
    
def main():
    classes = dict()
    telemetries = dict()
    threads = []
    tasklist = []
    top = {}
    # read configuration file 
    parser = configparser.ConfigParser()
    found = parser.read(candidates)
    if not found:
        sys.exit("No configuration files found, aborting")
    logfile = os.path.join(webpath, "marvin.log")
    top['log'] = open(logfile, "a")
    msg = f"Marvin started at {datetime.now().strftime('%-m/%-d/%-y %-I:%M%p')}\n"
    top['log'].write(msg)
    top['log'].flush()
    os.chmod(logfile, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    for filename in os.listdir(modulepath):
        fullfilename = modulepath + "/" + filename
        if filename.endswith(".py") and not filename.startswith("__init__"):
            classname = os.path.splitext(filename)[0]
            try:
                importlib.import_module(classname)
            except:
                traceback.print_exc()
                sys.exit("Unable to import " + classname )
            try:
                for newclass in classList(classname):
                    classes[newclass[0]] = newclass[1]
            except:
                sys.exit("Unable to parse " + classname)

    # Set up the class with a queue to wait on
    for key,value in classes.items():
        try:
            newinstance = value(key)
        except:
            sys.exit("Topic is missing from class ", key)

        if (newinstance.telemetry != None):
            if (isinstance(newinstance.telemetry, list)):
                for t in newinstance.telemetry:
                    if (t not in telemetries):
                        telemetries[t] = dict()
                        telemetries[t]['instance'] = []
                    telemetries[t]['instance'].append(newinstance)
            else:
                if (newinstance.telemetry not in telemetries):
                    telemetries[newinstance.telemetry] = dict()
                    telemetries[newinstance.telemetry]['instance'] = []
                telemetries[newinstance.telemetry]['instance'].append(newinstance)
            newinstance.payload = q.Queue(0)
        tasklist.append(newinstance)

    client = mqtt.Client(client_id="marvind", userdata=telemetries) 
    client.username_pw_set(parser.get('broker', 'user'), parser.get('broker', 'password'))
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(parser.get('broker', 'broker'), int(parser.get('broker', 'port')), 60)
    # if we have a database section then create a database pool
    # example code for accessing database in threads
    # most likely the error is insufficient pools, suggest increasing pool_size in configuration file
    #    if top['db'] is not None:
    #        try:
    #            conn = top['db'].get_connection()
    #            cur = conn.cursor()
    #            cur.execute("SELECT DATABASE STUFF HERE;");
    #            conn.close()
    #        except mariadb.PoolError as e:
    #            top['log'].write(f"Unable to open database connection: {e}")
    #            top['log'].flush()
            

    if ('database' in parser):
        try:
            top['db'] = mariadb.ConnectionPool(
                host=parser.get('database', 'host',fallback='localhost'),
                user=parser.get('database', 'user',fallback=None),
                password=parser.get('database', 'password',fallback=None),
                database=parser.get('database', 'database',fallback=None),
                port=parser.getint('database', 'port',fallback=3306),
                pool_size=parser.getint('database', 'pool_size',fallback=5),
                pool_name='marvin_db')
        except mariadb.Error as e:
            msg = f"Unable to open database {parser.get('database', 'database',fallback='unspecified')}, {e}\n"
            top['log'].write(msg)
            top['log'].flush()
            top['db'] = None
    else:
        top['db'] = None    

    for task in tasklist:
        t = threading.Thread(target=task.run, args=(client,top,))
        t.daemon = True
        t.start()
        threads.append(t)

    # connect to MQTT to subscribe and publish
    client.loop_forever()
    
    
isDaemon = False
if ((len(sys.argv) > 1) and (sys.argv[1].lower() == '--daemon')):
    isDaemon = True

if (isDaemon):
    daemon = Daemonize(app="main", pid=pid, action=main)
    daemon.start()
else:
    main()
# marvin
marvin is a smarthome application that runs as a daemon on Linux. It watches and responds to MQTT events.
A lot of smarthome sensors adopted MQTT as the defacto standard. Even if the device I used didn't support MQTT, there was  always a way to do so. 

I tried most smarthome applications but encounter a technical cliff everytime if I wanted to do something a little different. Most of my devices are ESP8266 based, it does it job well but don't ask for the moon from it. I use Tasmota on some of them and it has a rudimentary language but it quickly became a logistical nightmare to manage. I shifted to having the IoT device output simple raw data. 

So marvin subscribes to the IoT device, then can do a more comprehensive calculation, which in turn publishes the result with a different subtopic.

For display and control, I use linux (raspberry pi 3B+) with chromium browser in kiosk mode. It's written in html, CSS and javascript to pick up these new publications and present them. I also have a web based control application from my smartphone.

marvin is written in python simply because of the robust number of interesting libraries you can get for it. 

It is organized as the main.py program and a modules directory. Inside the modules directory are individual files which are read in as separate classes and separate threads by the main program. Each file has one or more MQTT events it listens for and when triggered, it can perform various actions. It has access to database, files, and time. 

Here's some simple examples:

**Cheap Ricecooker** - my ricecooker has no autooff and can make a real mess if left on. A sonoff wall relay and current monitor notices when the rice cooker is turned on. It waits and if it notices if it has been on too long. If so, it sends the off command to the relay. It also sends a nag message to me that I forgot to shut the thing off. This is also one of my simplest inocuous scripts. 

**propane tank** - I have a Mopeka Ultrasonic Tank Level sensor on my large propane tank kind of far from my house. It uses BLE advertising (manufacture data) to beacon the liquid level of the tank in millimeters. I use an ESP32 nearby to read the BLE advertising and convert it into raw JSON. Marvin reads this and uses the fluids package (fluids.geometry) to convert the level into gallons remaining and percentage full values. These are sent to my wall mounted display. Much easier to notice than trudgeing out through the snow to read the meter. 

## install
The prerequisites are python3, mosquitto (mqtt broker), mariadb. For additional python libraries, use `pip3 install -r requirements.txt`. The propane tank script also uses the fluids package and requires `pip3 install fluids`.

The broker and database both need to be setup and marvin requires access to both. In the assets directory is marvin_default.conf file, copy this file to marvin.conf and edit it, replace anything with <> with what it wants (username, passwords, domain names and table name). After configuration is setup, run the install script as `sudo ./install.sh`. If it can't find it, you may have to change the execute priveledges with `sudo chmod +x install.sh`.

## debug
If it is currently running as a service, stop it with `sudo systemctl stop marvin` 

The scripts should now be located in /usr/local/share/marvin directory. cd into that directory, and run sudo python3 ./main.py. 

This will run it as an application not in the background. I always do this with any new script just to see if I put something in my code which wasn't exactly python. When satisfied that everything is python, then exit with control-C. Use of the log facility can also check for problems. Any string can be sent to the log file with 
```python
top['log'].write(string)
top['log'].flush()
```

The log file is written to /var/www/html/marvin/marvin.log and can be browsed with local web client if the webservice is enabled. 

I'd also recommend another handy tool for debugging is MQTT Explorer (Windows only).

## running daemon
The daemon runs as a service. After installing successfully and you've tested it and quit. Get the service found, started and enabled with:
```bash
sudo systemctl daemon-reload
sudo systemctl enable marvin
sudo systemctl start marvin
```

You can check the status with `sudo systemctl status marvin`. It should be active running; otherwise, stop and debug it. 

## writing modules
Each module is a class, it has an *\_\_init\_\_* function and a run function. The *\_\_init\_\_* function is passed name and must initialize telemetry, name and payload. modulename is assigned to the name passed into *\_\_init\_\_*, `classname = self.__class__.__name__`, payload is assigned to None. telemetry is the MQTT topic that the script wants to watch for.  You can watch multiple topics by assigning telemtry to a list of topics. For example, in propane.py, the class is Propane and telemetry is set with `self.telemetry = ['tele/Propane/SENSOR', 'tele/Propane/STATE']`. Other class variables can be setup in *\_\_init\_\_*. 

The run function is passed client which is the MQTT client handle to the broker, and top dictionary. The top dictionary is access to logger handle top['log'] and database top['db']
The main program will execute run function and will not expect it to return rather block on a subscribed MQTT topic. So it usually has the form of:
```python
  while True:
    payload = self.payload.get()
```
The get blocks until the telemetry topic is sent something, once it receives a publication the json or raw data is put into payload and processed. Note that if topic was a string, payload is a string, if telemetry is set as a list, payload is a dictionary with the topic as the key.

## other examples
A few examples should be enough to get started with. Other examples:
2. Freezing - weather station reports freezing temperature, several items are powered up to avoid damage
3. Air Quality - convert particulate count into Air Quality Index (uses aqi library)
4. pumps - well, sump, sewage all have pumps - if any run too long it's something that needs addressing.

## how it works

main.py still uses daemonize but this is probably no longer a requirement. It does make debugging easier. 

First, it reads the configuration file and connects to MQTT broker and database. It then scans the modules directory for python files and imports them. For each one, it will grab the telemetry instance variable building a table of all topics. It sets up a queue for each class that the run method in the script can block on. All topics in the table are then subscribed to. If a topic is published, the triggered topic will put it's payload into each of the queues that is looking for that topic as event. That is, a single topic may unblock multiple threads. 
It passes the MQTT object, database connection and log file to each script. The MQTT object can be published to with new topic. 







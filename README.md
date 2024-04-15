# marvin
smarthome controller run as a daemon on Linux. It watches and responds to MQTT events.
So lots of custom smarthome sensors adopted MQTT as the defacto standard. Even if the device I used didn't support MQTT, there was generally a way available to do so. 
I tried most smarthome applications but ended up with html and javascript as my control and display medium. What I was missing was actual automation. Some IoT firmware had a rudimetary language but managing a lot of seperate devices with different programs and configurations was kind of nightmare. 

This is where marvin came in. I run it from the same server that my broker does. It runs as a daemon and as a service. I use daemonize but that probably is no longer a requirement. 
I chose python simply because of the robust number of interesting libraries you can get for it. 
It is organized as the main program and a modules directory. Inside the modules directory are individual files which are read in as separate classes and separate threads by the main program. Each file has one or more MQTT events it listens for and when triggered, it can perform various actions. It has access to database, files and can publish to the MQTT broker. 

Here's some simple examples:

**Cheap Ricecooker** - my ricecooker has no autooff and can make a real mess if left on. A sonoff wall relay and current monitor notices when the rice cooker is turned on. It waits and if it notices it's been on too long, it sends the off command to the relay. It also sends a nag message to me that I forgot to shut the thing off. This is also one of my simplest inocuous scripts. 

**propane tank** - I have a Mopeka Ultrasonic Tank Level sensor on my large propane tank situated kind of far from my house. It uses BLE advertising (manufacture data) to beacon the current level of the tank, that is the height of propane in millimeters inside the tank. I use an ESP32 nearby to read the BLE advertising and convert it into raw JSON. Marvin reads this and uses the fluids package (fluids.geometry) to convert the level into gallons remaining and percentage full values. These are sent to my wall mounted display. Much easier to notice than trudgeing out through the snow to read the meter. 

## install
The prerequisites are python3, mosquitto (mqtt broker), mariadb. For additional python libraries, use `pip3 install -r requirements.txt`. The propane tank script also uses the fluids package and requires `pip3 install fluids`.

The broker and database both need to be setup and marvin requires access to both. In the assets directory is marvin_default.conf file, copy this file to marvin.conf and edit it, replace anything with <> with what it wants (username, passwords, domain names and table name). After configuration is setup, run the install script as `sudo ./install.sh`. If it can't find it, you may have to change the execute priveledges with `sudo chmod +x install.sh`.

## debug
It should now be located in /usr/local/share/marvin directory. cd into that directory, and run sudo python3 ./main.py. If it is already running as a service, stop it with `systemctl stop marvin`

This will run it as an application not in the background. I always do this with any new script just to see if I put something in my code which wasn't exactly python. When satisfied that everything is python, then exit with control-C. Use of the log facility can also check for problems. Any string can be sent to the log file with 
```python
top['log'].write(msg)
top['log'].flush()
```

I put the log file at /var/www/html/marvin and can be browsed as local web. I'd recommend another handy tool for debugging is MQTT Explorer (Windows only).

## running daemon
The daemon runs as a service. After installing successfully and you've tested it and quit. Get the service found, started and enabled with:
```bash
sudo systemctl daemon-reload
sudo systemctl enable marvin
sudo systemctl start marvin
```

You can check the status with `sudo systemctl status marvin`

## writing modules
Each module is a class, it has an *\_\_init\_\_* function and a run function. The *\_\_init\_\_* function is passed name and must initialize telemetry, name and payload. name is always assigned to the name passed into *\_\_init\_\_*, payload is assigned to None. telemetry is the MQTT topic that the script wants to watch for.  You can watch multiple topics by assigning telemtry to a list of topics. For example, in propane.py, the class is Propane and telemetry is set with `self.telemetry = ['tele/Propane/SENSOR', 'tele/Propane/STATE']`. Other class variables can be setup in *\_\_init\_\_*. 

The run function is passed client which is the MQTT client handle to the broker, and top dictionary. The top dictionary is access to logger handle top['log'] and database top['db']
The main program will execute run function and will not expect it to return rather block on a subscribed MQTT topic. So it usually has the form of:
```python
  while True:
    payload = self.payload.get()
```
The get blocks until the telemetry topic is sent something, once it receives a publication the json or raw data is put into payload and processed. Note that if topic was a string, payload is a string, if telemetry is set as a list, payload becomes an ordered list, that is for the above telemetry example self.telemetry[0] is the payload for 'tele/Propane/SENSOR'. 


  




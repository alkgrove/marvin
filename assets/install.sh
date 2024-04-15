#!/usr/bin/bash

# cd marvin/assets
# suggest first creating marvin.conf by editing marvin_default.conf
# install.sh needs to be executable with sudo +x install.sh
# after creating marvin.conf run
# sudo ./install.sh
# moves all files from local install into /usr/local folders
# runs as a service
# then run this script. 
# variables to customize 
if [[ $EUID -ne 0 ]]; then
    echo "Run as root or sudo ./install.sh" 
    exit;
fi

if [ ! -f ./marvin.conf ]
then
    echo "Create marvin.conf by editing marvin_default.conf and saving as marvin.conf";
    echo "marvin.conf must be customized for username and passwords"
    echo "for mqtt broker and database. Python3, mosquitto and mariadb need to be"
    echo "installed prior to installing marvin"
    exit;
else 
    if [ ! -f /usr/local/etc/marvin.conf ]
    then 
        cp marvin.conf /usr/local/etc
        chmod 640 /usr/local/etc/marvin.conf
        chown root:root /usr/local/etc/marvin.conf
        echo "config file copied to /usr/local/etc/marvin.conf"
    fi
fi

cp marvin.service /lib/systemd/system
echo "copy service file to /lib/systemd/system and linked to /etc/systemd/system/marvin.service"
chmod 644 /lib/systemd/system/marvin.service
chown root:root /lib/systemd/system/marvin.service
[ -f /etc/systemd/system/marvin.service ] &&  rm -f /etc/systemd/system/marvin.service
ln -s /lib/systemd/system/marvin.service /etc/systemd/system/marvin.service
echo "scripts are copied to /usr/local/share/marvin"
[ ! -d /usr/local/share/marvin ] && mkdir /usr/local/share/marvin
cp -f ../*.py /usr/local/share/marvin
cp -Rf ../modules /usr/local/share/marvin
chown -R root:root /usr/local/share/marvin
chmod -R 750 /usr/local/share/marvin


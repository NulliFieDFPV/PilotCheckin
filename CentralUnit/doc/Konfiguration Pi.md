How To Pi


---------------------------------------------------------------------------------
Image installieren
---------------------------------------------------------------------------------
als root:
aptitude update
aptitude upgrade
---------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Webserver
---------------------------------------------------------------------------------
aptitude install apache2
aptitude install php5

/etc/apache2/apache2.conf
Ganz unten: Include /etc/phpmyadmin/apache.conf
sudo /etc/init.d/apache2 restart
---------------------------------------------------------------------------------


---------------------------------------------------------------------------------
Datenbankserver
---------------------------------------------------------------------------------
aptitude install mysql-server

User: root
Pass: pilotcheckin

aptitude install phpmyadmin
Pass für administrativer User:
pilotcheckin

Pass für Application User:
pilotcheckin
---------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Python
---------------------------------------------------------------------------------
sudo apt-get install git
sudo apt-get install python-mysqldb
sudo apt-get install mython-serial
sudo apt-get install python-smbus python-dev
sudo apt-get install i2c-tools
sudo apt-get install libi2c-dev 
sudo apt-get install python-pip

sudo pip install --upgrade OPi.GPIO


sudo nano /usr/local/lib/python2.7/dist-packages/OPi/GPIO.py

in setup() vor sysfs.direction()

time.sleep(0.1)
---------------------------------------------------------------------------------

---------------------------------------------------------------------------------
I2C aktivieren
---------------------------------------------------------------------------------
sudo nano /etc/modules
i2c-dev
---------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Userrechte
---------------------------------------------------------------------------------
user: pilot
pass: pilot
sudo groupadd gpio &&
sudo groupadd i2c &&
sudo groupadd spi &&
sudo usermod -aG gpio,i2c,spi <USER>
---------------------------------------------------------------------------------

---------------------------------------------------------------------------------
UDEV-Regeln
---------------------------------------------------------------------------------
sudo nano /etc/udev/rules.d/99-gpio.rules
KERNEL=="gpio*", RUN="/bin/sh -c 'chgrp -R gpio /sys/%p /sys/class/gpio && chmod -R g+w /sys/%p /sys/class/gpio'"

sudo nano /etc/udev/rules.d/99-spidev.rules
KERNEL=="spidev*", RUN="/bin/sh -c 'chgrp -R spi /dev/spidev* && chmod -R g+rw /dev/spidev*'"

sudo nano /etc/udev/rules.d/99-i2c.rules
KERNEL=="i2c*", RUN="/bin/sh -c 'chgrp -R i2c /dev/i2c* && chmod -R g+rw /dev/i2c*'"
---------------------------------------------------------------------------------

---------------------------------------------------------------------------------
PilotCheckin
---------------------------------------------------------------------------------
cd /home/pilot/
git clone git@github.com:NulliFieDFPV/PilotCheckin.git
cd PilotCheckin

sudo mkdir /etc/CentralUnit
sudo cp -r CentralUnit/ /etc/CentralUnit 

chmod +x /etc/CentralUnit/cArduserver.py /etc/CentralUnit/cRaceStarter.py


---------------------------------------------------------------------------------
Arduserver als Dienst installieren
---------------------------------------------------------------------------------

sudo nano /etc/systemd/system/pyarduserver.service

[Unit]
Description=My Python PilotCheckin
After=syslog.target

[Service]  
Type=simple
User=pyarduuser
Group=pyarduuser
WorkingDirectory=/etc/CentralUnit
ExecStart=/etc/CentralUnit/cArduserver.py
SyslogIdentifier=pilotcheckin
StandardOutput=syslog
StandardError=syslog 
Restart=always
RestartSec=3  

[Install]
WantedBy=multi-user.target
---------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Racestarter als Dienst installieren
---------------------------------------------------------------------------------

sudo nano /etc/systemd/system/pyracestarter.service

[Unit]
Description=My Python RaceStarter
After=syslog.target

[Service]  
Type=simple
User=pyarduuser
Group=pyarduuser
WorkingDirectory=/etc/CentralUnit
ExecStart=/etc/CentralUnit/cRaceStarter.py
SyslogIdentifier=racestarter
StandardOutput=syslog
StandardError=syslog 
Restart=always
RestartSec=3  

[Install]
WantedBy=multi-user.target
---------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Log Rotate für Arduserver
---------------------------------------------------------------------------------
sudo nano /etc/logrotate.d/pilotcheckin

/var/log/pilotcheckin.log {
    su root syslog
    daily
    rotate 5
    compress
    delaycompress
    missingok
    postrotate
        systemctl restart rsyslog > /dev/null
    endscript
}
---------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Log Rotage für Racestarter
---------------------------------------------------------------------------------
sudo nano /etc/logrotate.d/racestarter


/var/log/racestarter.log {
    su root syslog
    daily
    rotate 5
    compress
    delaycompress
    missingok
    postrotate
        systemctl restart rsyslog > /dev/null
    endscript
}
---------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Log Rotate neu starten
---------------------------------------------------------------------------------
systemctl restart rsyslog
---------------------------------------------------------------------------------

---------------------------------------------------------------------------------
Eigene Log Dateien
---------------------------------------------------------------------------------
sudo nano /etc/rsyslog.d/50-default.conf

:programname,isequal,"pilotcheckin"         /var/log/pilotcheckin.log
& ~

:programname,isequal,"racestarter"         /var/log/racestarter.log
& ~

---------------------------------------------------------------------------------


---------------------------------------------------------------------------------


How To Pi

Image installieren

als root:
aptitude update
aptitude upgrade

Webserver
aptitude install apache2
aptitude install php5

/etc/apache2/apache2.conf
Ganz unten: Include /etc/phpmyadmin/apache.conf
sudo /etc/init.d/apache2 restart


Datenbankserver
aptitude install mysql-server

root
pilotcheckin

aptitude install phpmyadmin
pw für administrativer user:
pilotcheckin

pw für application user:
pilotcheckin

Python
aptitude install git
aptitude install python-mysqldb
aptitude install mython-serial
sudo apt-get install python-smbus python-dev
sudo apt-get install i2c-tools
sudo apt-get install libi2c-dev 


I2C aktivieren
sudo nano /etc/modules
i2c-dev


Userrechte
user: pilot
pass: pilot
sudo groupadd gpio &&
sudo groupadd i2c &&
sudo groupadd spi &&
sudo usermod -aG gpio,i2c,spi <USER>


sudo nano /etc/udev/rules.d/99-gpio.rules
KERNEL=="gpio*", RUN="/bin/sh -c 'chgrp -R gpio /sys/class/gpio* && chmod -R g+w /sys/class/gpio*'"

sudo nano /etc/udev/rules.d/99-spidev.rules
KERNEL=="spidev*", RUN="/bin/sh -c 'chgrp -R spi /dev/spidev* && chmod -R g+rw /dev/spidev*'"

sudo nano /etc/udev/rules.d/99-i2c.rules
KERNEL=="i2c*", RUN="/bin/sh -c 'chgrp -R i2c /dev/i2c* && chmod -R g+rw /dev/i2c*'"


#!/usr/bin/env bash
echo -e "Installing 'Python' dependencies!\n"
yes | pip3 install -r requirements.txt

echo -e "Installing 'dnsiff' dependency!\n"
yes | sudo apt-get install dsniff             # To block internet via 'arpspoof' module

echo -e "Installing 'supervisor' dependency!\n"
PATH_SRC=./supervisord/aroundtheclock.conf
PATH_DST=/etc/supervisor/conf.d/aroundtheclock.conf
yes | sudo apt-get install supervisor         # To ensure reliability of running script
sudo cp $PATH_SRC $PATH_DST
read -p "Please hit ENTER to modify the paths for the 'supervisorctl' config file!"
vi $PATH_DST
echo -e "The config file located at $PATH_DST has been modified!\n"

echo -e "Enabling 'supervisor' to run automatically on startup"
systemctl enable supervisor.service
# /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf   # Troubleshoot

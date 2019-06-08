#!/usr/bin/env bash
echo -e "Creating a 'Python' virtual environment and installing dependencies!\n"
pyvenv venv
source ./venv/bin/activate
yes | pip3 install -r requirements.txt
mkdir output

echo -e "Installing 'dnsiff' dependency!\n"
yes | sudo apt-get install dsniff             # To block internet via 'arpspoof' module

echo -e "Installing 'supervisor' dependency!\n"
PATH_SRC=./supervisord.conf
PATH_TMP=./supervisord_tmp.conf
PATH_DST=/etc/supervisor/conf.d/aroundtheclock.conf
yes | sudo apt-get install supervisor         # To ensure reliability of running script
sudo cp $PATH_SRC $PATH_TMP
sed -i "s|<PATH_TO_PROJECT_ROOT>|$(pwd)|g" $PATH_TMP
sudo mv $PATH_TMP $PATH_DST
echo -e "A new supervisor config file is located at $PATH_DST!\n"

echo -e "Enabling 'supervisor' to run automatically on startup"
sudo systemctl enable supervisor.service
# /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf   # Troubleshoot

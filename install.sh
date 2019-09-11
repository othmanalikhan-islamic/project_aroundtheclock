#!/bin/bash
echo -e "\n>>> CHANGING PERMISSIONS ON RUN.SH..."
chmod u+x run.sh

echo -e "\n>>> INSTALLING PYTHON3..."
sudo apt install python3

echo -e "\n>>> CREATING A 'PYTHON' VIRTUAL ENVIRONMENT AND INSTALLING DEPENDENCIES..."
python3 -m venv virtual
source ./virtual/bin/activate
yes | pip3 install -r requirements.txt
mkdir output

echo -e "\n>>> INSTALLING 'DSNIFF' DEPENDENCY..."
yes | sudo apt install dsniff             # To block internet via 'arpspoof' module

echo -e "\n>>> INSTALLING 'SUPERVISOR' DEPENDENCY..."
PATH_SRC=./supervisord.conf
PATH_TMP=./supervisord_tmp.conf
PATH_DST=/etc/supervisor/conf.d/aroundtheclock.conf
yes | sudo apt install supervisor         # To ensure python script runs
sudo cp $PATH_SRC $PATH_TMP
sed -i "s|<PATH_TO_PROJECT_ROOT>|$(pwd)|g" $PATH_TMP
sudo mv $PATH_TMP $PATH_DST
echo -e "A new supervisor config file is located at $PATH_DST!\n"

echo -e "\n>>> ENABLING 'SUPERVISOR' TO RUN AUTOMATICALLY ON STARTUP..."
sudo systemctl enable supervisor.service
# /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf   # Troubleshoot
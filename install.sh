#!/bin/bash
echo -e "\n>>> INSTALLING PYTHON3..."
yes | sudo apt install python3

echo -e "\n>>> INSTALLING PYTHON PIP3..."
yes | sudo apt install python3-pip

echo -e "\n>>> INSTALLING PYTHON VIRTUAL ENVIRONMENT PACKAGE..."
yes | sudo apt install python3-venv

echo -e "\n>>> CREATING A PYTHON VIRTUAL ENVIRONMENT AND INSTALLING DEPENDENCIES..."
python3 -m venv virtual
source ./virtual/bin/activate
yes | pip3 install -r requirements.txt
mkdir output

echo -e "\n>>> INSTALLING 'DSNIFF' DEPENDENCY..."
yes | sudo apt install dsniff             # To block internet via 'arpspoof' module

echo -e "\n>>> CREATING A DAEMON USER 'AROUNDTHECLOCK'"
sudo useradd -r aroundtheclock -s /bin/false

echo -e "\n>>> INSTALLING AROUNDTHECLOCK AS A DAEMON..."
PATH_SRC=./aroundtheclock.service
PATH_DST=/lib/systemd/system/aroundtheclock.service
sudo cp $PATH_SRC $PATH_DST
sudo sed -i "s|<PATH_TO_PROJECT_ROOT>|$(pwd)|g" $PATH_DST

echo -e "\n>>> CHANGING PERMISSIONS ON AROUNDTHECLOCK RUN SCRIPT..."
chown aroundtheclock:aroundtheclock run.sh
chmod u+x run.sh

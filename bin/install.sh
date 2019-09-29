#!/bin/bash
echo -e "\n>>> INSTALLING OS DEPENDENCIES..."
while read -r dependency; do
  yes | sudo apt-get install $dependency
done < requirements_linux.txt

echo -e "\n>>> CREATING A PYTHON VIRTUAL ENVIRONMENT AND INSTALLING ITS DEPENDENCIES..."
python3 -m venv virtual
source ./virtual/bin/activate
yes | pip3 install -r requirements_python.txt

echo -e "\n>>> CREATING A DAEMON USER 'AROUNDTHECLOCK'"
sudo useradd -r aroundtheclock -s /bin/false

echo -e "\n>>> INSTALLING AROUNDTHECLOCK AS A DAEMON..."
PATH_SRC=./config/aroundtheclock.service
PATH_DST=/lib/systemd/system/aroundtheclock.service
sudo cp $PATH_SRC $PATH_DST
sudo sed -i "s|<PATH_TO_PROJECT_ROOT>|$(pwd)|g" $PATH_DST

echo -e "\n>>> CHANGING PERMISSIONS ON AROUNDTHECLOCK PROJECT..."
sudo chown -R aroundtheclock:aroundtheclock .
sudo chmod u+x bin/run.sh

echo -e "\n>>> ENABLING AROUNDTHECLOCK DAEMON..."
sudo systemctl enable aroundtheclock.service
sudo systemctl start aroundtheclock.service

#!/bin/bash
echo -e "\n>>> CREATING BATS DIRECTORY IN HOME DIRECTORY..."
cd ~ || exit
mkdir bats
cd bats || exit

echo -e "\n>>> CLONING GITHUB BATS REPOSITORY..."
git clone https://github.com/sstephenson/bats.git
cd bats || exit

echo -e "\n>>> INSTALLING BATS..."
sudo ./install.sh /usr/local

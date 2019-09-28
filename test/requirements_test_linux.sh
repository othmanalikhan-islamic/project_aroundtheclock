#!/bin/bash
cd ~ || exit
git clone https://github.com/sstephenson/bats.git
cd bats || exit
./install.sh /usr/local

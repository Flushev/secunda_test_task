#! /bin/bash -e

sudo apt update
sudo apt full-upgrade -y
sudo apt install -y default-libmysqlclient-dev python3-virtualenv pkg-config build-essential python3-dev

if [ -d "venv" ];
then
  sudo rm -rf venv
fi
sudo mkdir venv
sudo chown -R $USER:$USER ./
python3 -m virtualenv venv
source venv/bin/activate
pip install -U pip setuptools wheel
if [ -f "requirements.txt" ];
then
  pip install -r requirements.txt
fi

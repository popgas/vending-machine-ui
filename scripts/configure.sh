#!/bin/bash

python -m venv .env
pip install -r requirements.txt

sudo cp popgas.service /etc/systemd/system/
sudo cp popgas.timer /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable popgas.timer
sudo systemctl restart popgas.timer
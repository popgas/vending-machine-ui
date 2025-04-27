#!/bin/bash

cp popgas.service /etc/systemd/system/
cp popgas.timer /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable popgas.timer
sudo systemctl restart popgas.timer
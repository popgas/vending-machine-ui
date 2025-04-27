#!/bin/bash

cp popgas.service /etc/systemd/system/popgas.service
cp popgas.timer /etc/systemd/system/popgas.timer

sudo systemctl daemon-reload
sudo systemctl enable popgas.timer
sudo systemctl restart popgas.timer
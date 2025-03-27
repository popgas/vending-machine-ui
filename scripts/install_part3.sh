#!/bin/bash
cd ~
wget https://files.pythonhosted.org/packages/ce/bf/ff284a136b39cb1873c18e4fca4a40a8847c84a1910c5fb38c6a77868968/pyqt6-6.8.1.tar.gz

tar -xzf pyqt6-6.8.1.tar.gz
python -m venv .venv
source .env/bin/activate
pip install pyqt-builder
export PATH="$PATH:/opt/Qt/6.8.1-armv7l/bin"
cd ~/pyqt6-6.8.1
sip-wheel --confirm-license --verbose --qmake-setting 'QMAKE_LIBS_LIBATOMIC = -latomic'
pip install PyQt6-6.8.1-cp38-abi3-manylinux_2_28_x86_64.whl
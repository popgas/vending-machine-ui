#!/bin/bash
cd ~
wget https://download.qt.io/official_releases/qt/6.8/6.8.3/single/qt-everywhere-src-6.8.3.tar.xz
tar xf qt-everywhere-src-6.8.3.tar.xz
mkdir qt-everywhere-src-6.8.3/build
cd qt-everywhere-src-6.8.3/build

cmake -G Ninja \
-DCMAKE_INSTALL_PREFIX=/opt/Qt/6.8.1-armv7l \
-DQT_FEATURE_opengles2=ON \
-DQT_FEATURE_opengles3=ON \
-DQT_FEATURE_kms=ON \
-DQT_AVOID_CMAKE_ARCHIVING_API=ON ..

cmake --build . --parallel 4
cmake –-install .
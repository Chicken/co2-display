#!/usr/bin/env bash

DEVICE=/dev/ttyUSB0
ROOT="$(dirname "$(readlink -f $0)")/.."

rshell --port $DEVICE --quiet rm -r /pyboard/*

ampy --port $DEVICE put "$ROOT/boot/boot.py" /boot.py
ampy --port $DEVICE put "$ROOT/boot/main.py" /main.py

echo Done!

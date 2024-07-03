#!/usr/bin/env bash

DEVICE=/dev/ttyUSB0
ROOT="$(dirname "$(readlink -f $0)")/.."

echo Removing old code...
rshell --port $DEVICE --quiet rm -r /pyboard/src
echo Adding new code...
ampy --port $DEVICE put "$ROOT/src/" src/

echo Done!

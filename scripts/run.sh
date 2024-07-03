#!/usr/bin/env bash

DEVICE=/dev/ttyUSB0
ROOT="$(dirname "$(readlink -f $0)")/.."

"$ROOT"/scripts/upload.sh

echo Running...
pyboard --device $DEVICE -c "import src.main"

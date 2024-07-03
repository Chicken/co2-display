#!/usr/bin/env bash

ROOT="$(dirname "$(readlink -f $0)")/.."

rm -rf "$ROOT/.vscode/stub-types"
python3 -m pip install micropython-esp32-stubs==1.23.0.post1 --target "$ROOT/.vscode/stub-types" --no-user

#!/usr/bin/env bash

FIRMWARE="ESP32_GENERIC-20240602-v1.23.0.bin"
PORT="/dev/ttyUSB0"

wget "https://micropython.org/resources/firmware/$FIRMWARE"
esptool.py --chip esp32 --port "$PORT" erase_flash
esptool.py --chip esp32 --port "$PORT" --baud 460800 write_flash -z 0x1000 "$FIRMWARE"
rm "$FIRMWARE"

# CO2 display

Uses an [ESP32 One](https://www.waveshare.com/wiki/ESP32_One), [SSD1309](https://www.solomon-systech.com/product/ssd1309/),
[CO2L](https://docs.m5stack.com/en/unit/CO2L) ([SCD41](https://sensirion.com/products/catalog/SCD41)) and a random button.

## Pins

### SCD41

Wire | Pin No. | GPIO
--- | --- | ---
SCL | 5 | 23
SDA | 3 | 18

### SSD1309

Wire | Pin No. | GPIO
--- | --- | ---
DC | 22 | 0
RES | 11 | 19
SDA | 19 | 13
SCL | 23 | 14

### Button

Wire | Pin No. | GPIO
--- | --- | ---
3V3 | 15 | 2

## Running

1. Install esptool.py, ampy and rshell
1. Connect the board to your computer
1. Flash micropython to the board `./scripts/flash.sh`
1. Prepare the board `./scripts/prepare.sh`
1. Upload the code `./scripts/upload.sh`

### Development

- Have ampy, rshell and pyboard, yes I'm abusing three different tools because I like how they do different things
- Download stub types for the micropython environment `./scripts/stubs.sh`
- Run the code `./scripts/run.sh`

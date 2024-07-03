from micropython import const
from machine import Pin
from framebuf import FrameBuffer, MONO_VLSB 
from utime import sleep_ms

SSD1309_WIDTH = const(128)
SSD1309_HEIGHT = const(64)

DISPLAY_OFF = const(0xAE)
DISPLAY_ON = const(0XAF)

SET_MEMORY_ADDRESSING_MODE = const(0x20)
ADDRESSING_MODE_HORIZONTAL = const(0x00)
SET_SEGMENT_MAP_FLIPPED = const(0xA1)
SET_COM_OUTPUT_FLIPPED = const(0xC8)

class SSD1309:
    def __init__(self, spi, dc, rst):
        self.RST = rst
        self.RST.init(Pin.OUT, value=1)
        
        self.DC = dc
        self.DC.init(Pin.OUT, value=0)
        
        self.SPI = spi

        self.buffer = bytearray((SSD1309_WIDTH // 8) * SSD1309_HEIGHT)
        self.fb = FrameBuffer(self.buffer, SSD1309_WIDTH, SSD1309_HEIGHT, MONO_VLSB)
        self.clear()
        
        self.reset()
        for settings in (
            # make MONO_VLSB work
            SET_MEMORY_ADDRESSING_MODE, ADDRESSING_MODE_HORIZONTAL,
            # top left is 0,0
            SET_SEGMENT_MAP_FLIPPED,
            SET_COM_OUTPUT_FLIPPED,
            # turn on display (sleep by default after reset)
            DISPLAY_ON
        ):
            self.send_command(settings)

        self.show()

    def reset(self):
        self.RST.value(1)
        sleep_ms(10)
        self.RST.value(0)
        sleep_ms(10)
        self.RST.value(1)
        sleep_ms(10)

    def send_command(self, command):
        self.DC.value(0)
        self.SPI.write(bytearray([command]))

    def send_data(self, data):
        self.DC.value(1)
        self.SPI.write(data)

    def shutdown(self):
        self.clear()
        self.show()
        self.send_command(DISPLAY_OFF)
        self.SPI.deinit()

    def clear(self):
        self.fb.fill(0)

    def show(self):
        self.send_data(self.buffer)

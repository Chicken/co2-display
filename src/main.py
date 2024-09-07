from machine import Pin, I2C, SPI, reset
from time import ticks_ms, ticks_diff
from math import ceil
import asyncio

from src.scd41 import SCD41, Measurement
from src.ssd1309 import SSD1309
from src.data import Results

btn = Pin(2, Pin.IN)

i2c = I2C(0, scl=Pin(23), sda=Pin(18), freq=400000)
scd = SCD41(i2c)

spi: SPI = None # type: ignore
display: SSD1309 = None # type: ignore
def init_display():
    global spi, display
    spi = SPI(1, baudrate=10000000, sck=Pin(14), mosi=Pin(13))
    display = SSD1309(spi, Pin(0), Pin(19))
init_display()

scd.disable_asc()
scd.start_periodic_measurement()

past_results = Results()
past_three = []
previous_point = ticks_ms()
graphs = ["co2", "temperature", "relative_humidity"]
default_max_values = {
    "co2": 1000,
    "temperature": 50,
    "relative_humidity": 100
}
units = {
    "co2": "ppm",
    "temperature": "C",
    "relative_humidity": "H%"
}
display_on = True

GRAPH_TIME_FRAME = const(12 * 60) # minutes
GRAPH_TIME_PER_POINT = ceil(GRAPH_TIME_FRAME/128*60/5)*5*1000

loop = asyncio.get_event_loop()

def draw_value_text(val, unit, offset):
    display.fb.text(str(val), offset, 0)
    offset += len(str(val)) * 8
    display.fb.text(unit, offset + 2, 0)
    offset += len(unit) * 8 + 2 + 10
    return offset

def draw(measurement=None, graph=False):
    if not display_on:
        return

    if not measurement:
        if not len(past_three) and not len(past_results):
            return
        measurement = past_three[-1] if len(past_three) else past_results[-1]

    if graph: display.fb.fill(0)
    else: display.fb.rect(0, 0, 128, 8, 0, True)

    offset = 0
    offset = draw_value_text(measurement[graphs[0]], units[graphs[0]], offset)
    offset = draw_value_text(measurement[graphs[1]], units[graphs[1]], offset)
 
    if not graph or not len(past_results):
        display.show()
        return
    
    current_graph = graphs[0]
    max_val = max(default_max_values[current_graph], max(m[current_graph] for m in past_results))
    min_y = 9
    max_y = 63 - min_y
    graph_offset = 128 - len(past_results)

    for i in range(len(past_results)):
        previous = past_results[i - 1] if i > 0 else past_results[i]
        current = past_results[i]
        next = past_results[i + 1] if i < len(past_results) - 1 else past_results[i]

        previous_pos = min_y + (max_y - int(previous[current_graph] / max_val * max_y))
        current_pos = min_y + (max_y - int(current[current_graph] / max_val * max_y))
        next_pos = min_y + (max_y - int(next[current_graph] / max_val * max_y))

        display.fb.pixel(graph_offset + i, current_pos, 1)

        if previous_pos > current_pos:
            display.fb.vline(graph_offset + i, current_pos, previous_pos - current_pos, 1)
        if next_pos > current_pos:
            display.fb.vline(graph_offset + i, current_pos, next_pos - current_pos, 1)

    display.show()

async def update():
    global previous_point
    while True:
        try:
            if scd.is_data_ready():
                measurement = scd.read_measurement()
                past_three.append(measurement)
                if len(past_three) > 3:
                    past_three.pop(0)

                now = ticks_ms()
                if ticks_diff(now, previous_point) >= GRAPH_TIME_PER_POINT:
                    previous_point = now
                    past_results.append(Measurement.average(past_three))
                    if len(past_results) > 128:
                        past_results.pop(0)
                    past_results.save()
                    draw(measurement, graph=True)
                else:
                    draw(measurement, graph=False)
            await asyncio.sleep_ms(5000) # type: ignore
        except Exception as e:
            import sys
            sys.print_exception(e) # type: ignore
            loop.stop()
            break

async def button():
    global display_on
    is_pressed = False
    skip_press = False
    held_since = 0

    while True:
        if btn.value() and not is_pressed:
            is_pressed = True
            held_since = ticks_ms()
        elif not btn.value() and is_pressed:
            is_pressed = False
            if skip_press:
                skip_press = False
                continue
            if not display_on:
                display_on = True
                init_display()
                draw(graph=True)
                continue
            if ticks_diff(ticks_ms(), held_since) < 400:
                graphs.append(graphs.pop(0))
                draw(graph=True)
            else:
                display_on = False
                display.shutdown()
        
        if is_pressed and display_on and not skip_press and ticks_diff(ticks_ms(), held_since) > 4000:
            skip_press = True
            past_results.clear()
            draw(graph=True)

        await asyncio.sleep_ms(50)  # type: ignore

draw(graph=True)
loop.create_task(update())
loop.create_task(button())
loop.run_forever()

scd.stop_periodic_measurement()
scd.power_down()
display.shutdown()
reset()

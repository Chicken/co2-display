from time import sleep_ms
from micropython import const

SCD41_DEFAULT_ADDRESS = 0x62

SCD41_CMD_IS_DATA_READY = const(0xE4B8)
SCD41_READ_MEASUREMENT = const(0xEC05)
SCD41_STOP_PERIODIC_MEASUREMENT = const(0x3F86)
SCD41_START_PERIODIC_MEASUREMENT = const(0x21B1)
SCD41_POWER_DOWN = const(0x36E0)
SCD41_SET_AUTOMATIC_SELF_CALIBRATION = const(0x2416)

class Measurement:
    def __init__(self, co2, temperature, relative_humidity):
        self.co2 = round(co2)
        self.temperature = round(temperature, 1)
        self.relative_humidity = round(relative_humidity)

    def __getitem__(self, key):
        if key == "co2": return self.co2
        if key == "temperature": return self.temperature
        if key == "relative_humidity": return self.relative_humidity
        raise KeyError(key)
    
    def serialize(self):
        return f"{str(self.co2)},{str(self.temperature)},{str(self.relative_humidity)}"

    @staticmethod
    def deserialize(string):
        parts = string.split(",")
        return Measurement(int(parts[0]), float(parts[1]), int(parts[2]))

    @staticmethod
    def average(measurements):
        co2 = sum(m.co2 for m in measurements) // len(measurements)
        temperature = round(sum(m.temperature for m in measurements) / len(measurements), 1)
        relative_humidity = sum(m.relative_humidity for m in measurements) // len(measurements)
        return Measurement(co2, temperature, relative_humidity)

class SCD41:
    def __init__(self, i2c, address = SCD41_DEFAULT_ADDRESS):
        self.address = address
        self.i2c = i2c
        self.stop_periodic_measurement()

    def is_data_ready(self):
        self.send_command(SCD41_CMD_IS_DATA_READY)
        buf = self.read_reply(1)
        return not (buf[0] & 0x07ff == 0)

    def read_measurement(self):
        self.send_command(SCD41_READ_MEASUREMENT)
        buf = self.read_reply(3)
        co2 = buf[0]
        temperature = -45 + 175 * (buf[1] / (2**16 - 1))
        relative_humidity = 100 * (buf[2] / (2**16 - 1))
        return Measurement(co2, temperature, relative_humidity)

    def stop_periodic_measurement(self):
        self.send_command(SCD41_STOP_PERIODIC_MEASUREMENT)
        sleep_ms(500)

    def start_periodic_measurement(self):
        "5s interval"
        self.send_command(SCD41_START_PERIODIC_MEASUREMENT)
    
    def power_down(self):
        self.send_command(SCD41_POWER_DOWN)

    def disable_asc(self):
        self.send_command(SCD41_SET_AUTOMATIC_SELF_CALIBRATION, 0)

    def send_command(self, cmd, data = None):
        if data:
            buf = bytearray(5)
            buf[0] = (cmd >> 8) & 0xFF
            buf[1] = cmd & 0xFF
            buf[2] = (data >> 8) & 0xFF
            buf[3] = data & 0xFF
            buf[4] = crc8(buf[2:4])
            self.i2c.writeto(self.address, buf)
        else:
            self.i2c.writeto(self.address, bytearray([
                (cmd >> 8) & 0xFF,
                cmd & 0xFF
            ]))
        sleep_ms(1)

    def read_reply(self, reply_words):
        buf = bytearray(reply_words * 3)
        self.i2c.readfrom_into(self.address, buf)
        reply = [0] * reply_words;
        for i in range(0, len(buf), 3):
            if crc8(buf[i : i + 2]) != buf[i + 2]:
                raise RuntimeError("Reply CRC failed")
            reply[i // 3] = (buf[i] << 8) | buf[i + 1]
        return reply

CRC_POLYNOMIAL = const(0x31)
CRC_INIT = const(0xFF)
def crc8(buffer):
    crc = CRC_INIT
    for byte in buffer:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80: crc = (crc << 1) ^ CRC_POLYNOMIAL
            else: crc = crc << 1
    return crc & 0xFF

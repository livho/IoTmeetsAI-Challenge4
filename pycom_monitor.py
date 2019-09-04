# -*- coding: utf-8 -*-

# Copyright (C) 2019 IoT Meets AI Team Challenge 4
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from machine import I2C, Pin, UART

from lib import adafruit_am2320, adafruit_gps, sds011, adafruit_sgp30, ssd1306


def init_i2c(baudrate = 100000):
    """
    Initialize I2C bus
    :return:
    """
    i2c = I2C(0, I2C.MASTER)
    i2c.init(I2C.MASTER, baudrate=baudrate)

    return i2c


def temperature_humidity(n_try_max = 10):
    """
    Retrieve temperature (Celsius) and relative humidity form a pycom board,
    these sensors are a bit flakey, its ok if the readings fail
    :return: the temperature and the humidity
    """
    # init board params
    i2c = init_i2c()
    am = adafruit_am2320.AM2320(i2c)

    success = False
    n_try = 0

    while not success and n_try < n_try_max:
        try:
            success = True
            return am.temperature, am.relative_humidity
        except Exception:
            n_try += 1

    return None


def co2_tvoc():
    """
    Retrieve CO2 and TVOC from a pycom board
    :return: the co2 and tvoc
    """
    i2c = init_i2c()

    # Create library object on our I2C port
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

    # Initialize SGP-30 internal drift compensation algorithm.
    sgp30.iaq_init()

    return sgp30.co2eq, sgp30.tvoc


def latitude_longitude_altitude(update_rate = 1000):
    """
    Retrieve location data from a pycom board
    :return: x, y and z absolute coordinates
    """
    # Initialize UART
    uart = UART(1, baudrate=9600, timeout_chars=3000, pins=('P4', 'P3'))

    # Instanciate a Pin object linked to the enable pin of the GPS
    en_pin = Pin('P23', mode=Pin.OUT)

    # Instantiaite a GPS object
    gps = adafruit_gps.GPS(uart, en_pin)

    # Turns ON GPS (turn off using gps.disable())
    gps.enable()

    # Turn on the basic GGA and RMC info (what you typically want)
    gps.send_command('PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

    # Set update rate
    gps.send_command('PMTK220,' + str(update_rate))

    # Make sure to call gps.update() as often as possible to prevent loss
    # of data.
    # This returns a bool that's true if it parsed new data.
    if gps.update() and gps.has_fix:
        return gps.longitude, gps.latitude, gps.altitude_m
    else:
        return None


def bootstrap_pm10_pm25():
    """
    Bootstrap dust on a pycom board
    :return: True or False weather the fan strated
    """
    # Initialize UART pins(TX,RX)
    uart = UART(2, baudrate=9600, pins=('P21', 'P22'))

    # Instantiate a SDS011 object
    dust_sensor = sds011.SDS011(uart)

    # Instanciate a Pin object linked to the enable pin of the boost converter
    # (that supplies 5V to the SDS011)
    boost_en = Pin('P8', mode=Pin.OUT)

    # Stop fan
    dust_sensor.sleep()

    # Turns ON boost converter
    boost_en.value(1)
    # Turns on fan
    try:
        dust_sensor.wake()
        return True
    except Exception:
        return False


def read_pm10_pm25():
    """
    Retrieve dust measurements from a pycom board
    :return: the pm10 and pm25 measures
    """
    # Initialize UART pins(TX,RX)
    uart = UART(2, baudrate=9600, pins=('P21', 'P22'))

    # Instantiate a SDS011 object
    dust_sensor = sds011.SDS011(uart)

    # Instanciate a Pin object linked to the enable pin of the boost converter
    # (that supplies 5V to the SDS011)
    boost_en = Pin('P8', mode=Pin.OUT)

    # Get the measure
    status = dust_sensor.read()
    pkt_status = dust_sensor.packet_status

    # Stop fan
    dust_sensor.sleep()
    boost_en.value(0)  # Turns OFF boost converter

    if status == 'NOK':
        return None
    elif pkt_status == 'NOK':
        return None
    else:
        return dust_sensor.pm10, dust_sensor.pm25


def print_lcd(msg):
    """

    :param msg:
    :return:
    """
    i2c = init_i2c()

    # Initialize the reset pin
    res_pin = Pin('P11', mode=Pin.OUT)

    # Initialize the SSD1306 display
    d = ssd1306.SSD1306_I2C(64, 48, i2c, res=res_pin)

    # Power on and clear screen
    d.poweron()
    d.fill(0)

    # Add text
    d.text(string=str(msg), x=0, y=0)

    # Update the screen and power it Off
    d.show()
    d.poweroff()

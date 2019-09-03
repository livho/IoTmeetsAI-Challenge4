#
#    Project : "Station de qualité de l'air Lora"
#
#    Copyright (C) 2019  Yohann LE GALL & Sergio QUINTERO
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


import time
from machine import I2C
import adafruit_am2320

#Initialize the I2C bus
i2c = I2C(0, I2C.MASTER)
i2c.init(I2C.MASTER, baudrate=100000)

#Initialize the AM2320 sensor
am = adafruit_am2320.AM2320(i2c)

#Number of reading tentatives, as this sensor does not always respond...
n_try_max = 10

while True:
    success = False
    n_try = 0

    while(not success and n_try < n_try_max):
        try:
            print("Temperature: ", am.temperature)
            print("Humidity: ", am.relative_humidity)
            success = True
        except:
            # These sensors are a bit flakey, its ok if the readings fail
            n_try += 1

    #Probing this sensor too often makes it crash...
    #Let us do that once per second
    time.sleep(1)

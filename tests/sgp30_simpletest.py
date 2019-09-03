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



""" Example for using the SGP30 with CircuitPython and the Adafruit library"""

import time
from machine import I2C
import adafruit_sgp30

#Initialize I2C bus
i2c = I2C(0, I2C.MASTER)
i2c.init(I2C.MASTER, baudrate=100000)

#Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

print("SGP30 serial #", [hex(i) for i in sgp30.serial])

#Initialize SGP-30 internal drift compensation algorithm.
sgp30.iaq_init()
#Retrieve previously stored baselines, if any (helps the compensation algorithm).
try:
    f_co2 = open('co2eq_baseline.txt', 'r')
    f_tvoc = open('tvoc_baseline.txt', 'r')

    co2_baseline = int(f_co2.read())
    tvoc_baseline = int(f_tvoc.read())
    #Use them to calibrate the sensor
    sgp30.set_iaq_baseline(co2_baseline, tvoc_baseline)

    f_co2.close()
    f_tvoc.close()
except:
    print('Impossible to read SGP30 baselines!')

#Store the time at which last baseline has been saved
baseline_time = time.time()

while True:
    print('co2eq = ' + str(sgp30.co2eq) + ' ppm \t tvoc = ' + str(sgp30.tvoc) + ' ppb')

    #Baselines should be saved every hour, according to the doc.
    if(time.time() - baseline_time >= 3600):
        print('Saving baseline!')
        baseline_time = time.time()

        f_co2 = open('co2eq_baseline.txt', 'w')
        f_tvoc = open('tvoc_baseline.txt', 'w')

        f_co2.write(str(sgp30.baseline_co2eq))
        f_tvoc.write(str(sgp30.baseline_tvoc))

        f_co2.close()
        f_tvoc.close()

    #A measurement should be done every 60 seconds, according to the doc.
    time.sleep(1)

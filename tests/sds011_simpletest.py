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


from machine import UART
from machine import Pin
import time
import sds011

#Initialize UART    pins(TX,RX)
uart = UART(2, baudrate=9600, pins=('P21','P22'))

#Instantiate a SDS011 object
dust_sensor = sds011.SDS011(uart)

#Instanciate a Pin object linked to the enable pin of the boost converter
#(that supplies 5V to the SDS011)
boost_en = Pin('P8', mode=Pin.OUT)

#Stop fan
dust_sensor.sleep()

while True:

    #Datasheet says to wait for at least 30 seconds.
    print('Start fan for 30 seconds.')
    #Turns ON boost converter
    boost_en.value(1)
    #Turns on fan
    dust_sensor.wake()
    time.sleep(30)

    status = dust_sensor.read()
    pkt_status = dust_sensor.packet_status

    #Stop fan
    dust_sensor.sleep()

    if(status == 'NOK'):
        print('Measurement failed.')
    elif(pkt_status == 'NOK'):
        print('Received corrupted data.')
    else:
        print('PM25: ', dust_sensor.pm25)
        print('PM10: ', dust_sensor.pm10)

    #Turns OFF boost converter
    boost_en.value(0)

    #We do not want to measure too often, as this sensor's fan consumption has
    #a strong impact on the battery
    time.sleep(10)

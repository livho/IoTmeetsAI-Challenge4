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


# Simple GPS module demonstration.
# Will wait for a fix and print a message every second with the current location
# and other details.
from machine import UART
from machine import Pin
import utime as time

import adafruit_gps

#Initialize UART
uart = UART(1, baudrate=9600, timeout_chars=3000, pins=('P4', 'P3'))

#Instanciate a Pin object linked to the enable pin of the GPS
en_pin = Pin('P23', mode=Pin.OUT)

#Instantiaite a GPS object
gps = adafruit_gps.GPS(uart, en_pin)

#Turns ON GPS (turn off using dps.disbale())
gps.enable()

# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command('PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Set update rate to once a second (1hz).
gps.send_command('PMTK220,1000')
# Set update rate to once every two second (0.5hz).
#gps.send_command('PMTK220,2000')
# Set update rate to twice a second (2hz).
#gps.send_command('PMTK220,500')

# Main loop runs forever printing the location, etc. every second.
last_print = time.ticks_ms()
while True:
    # Make sure to call gps.update() as often as possible to prevent loss
    # of data.
    # This returns a bool that's true if it parsed new data.
    gps.update()
    # Every second print out current location details if there's a fix.
    current = time.ticks_ms()
    if time.ticks_diff(last_print, current) >= 1000:
        last_print = current

        if not gps.has_fix:
            # Try again if we don't have a fix yet.
            print('Waiting for fix...')
            continue

        # We have a fix! (gps.has_fix is true)
        # Print out details about the fix like location, date, etc.
        print('=' * 40)  # Print a separator line.
        print('Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}'.format(
            gps.timestamp_utc[1],   # Grab parts of the time from the
            gps.timestamp_utc[2],  # struct_time object that holds
            gps.timestamp_utc[0],  # the fix time.  Note you might
            gps.timestamp_utc[3],  # not get all data like year, day,
            gps.timestamp_utc[4],   # month!
            gps.timestamp_utc[5]))
        print('Latitude: {} degrees'.format(gps.latitude))
        print('Longitude: {} degrees'.format(gps.longitude))
        print('Fix quality: {}'.format(gps.fix_quality))
        # Some attributes beyond latitude, longitude and timestamp are optional
        # and might not be present.  Check if they're None before trying to use!
        if gps.satellites is not None:
            print('# satellites: {}'.format(gps.satellites))
        if gps.altitude_m is not None:
            print('Altitude: {} meters'.format(gps.altitude_m))
        if gps.track_angle_deg is not None:
            print('Speed: {} knots'.format(gps.speed_knots))
        if gps.track_angle_deg is not None:
            print('Track angle: {} degrees'.format(gps.track_angle_deg))
        if gps.horizontal_dilution is not None:
            print('Horizontal dilution: {}'.format(gps.horizontal_dilution))
        if gps.height_geoid is not None:
            print('Height geo ID: {} meters'.format(gps.height_geoid))

# -*- coding: utf-8 -*-
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

"""
In this module is the configuration of the LoPy4 when it boots, the interfaces and hardware features availables at the booting
"""
# boot.py -- run on boot-up
from machine import Pin
import network
import pycom

#Turn off heartbeat for built-in LED
pycom.heartbeat(False)

#Turn off bluetooth
bt = network.Bluetooth()
bt.deinit()

#Turn OFF WiFi
wlan = network.WLAN(mode=network.WLAN.STA)
wlan.deinit()

print('Ending boot file')

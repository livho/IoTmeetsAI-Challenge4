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
from machine import Pin
from lib import ssd1306

#Initialize the I2C bus
i2c = I2C(0, I2C.MASTER)
i2c.init(I2C.MASTER, baudrate=100000)

#Initialize the reset pin
res_pin = Pin('P11', mode=Pin.OUT)

#Initialize the SSD1306 display
d = ssd1306.SSD1306_I2C(64, 48, i2c, res=res_pin)

#Note: the screen can be turned off using:
#d.poweroff()
#It can then be powered on again using:
#d.poweron()

l1_pos = 0  #1st line
l2_pos = 10 #2nd line
l3_pos = 20 #3rd line
l4_pos = 30 #4th line

while True:
    #Clear screen
    d.fill(0)

    #Add text
    d.text('Welcome', 0, l1_pos)
    d.text('to IIoT', 0, l2_pos)
    d.text('Summer', 0, l3_pos)
    d.text('school!', 0, l4_pos)

    #Update the screen
    d.show()

    #Translate text vertically by one pixel for the next iteration
    l1_pos = (l1_pos + 1)%50
    l2_pos = (l2_pos + 1)%50
    l3_pos = (l3_pos + 1)%50
    l4_pos = (l4_pos + 1)%50

    #Updating the screen too often can bring instabilities in the I2C bus...
    time.sleep(1)

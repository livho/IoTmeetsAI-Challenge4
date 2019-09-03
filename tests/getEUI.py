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


from network import LoRa
import pycom

# Set Lora mode
lora = LoRa(mode=LoRa.LORAWAN)

# Get the mac adress of the pycom
mac = lora.mac()

# Print it
print ('devEUI: ',  end='')
for i in range (0,  8):
        print(hex(mac[i]), end='-')
print ()

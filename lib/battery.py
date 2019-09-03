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
This module provides a method to check the status of the battery
"""

from machine import ADC

class Battery:
    """A class to monitor a 3.7v Lithium-polymer battery.
    Caution: make sure that internal reference voltage have been calibrated!

    :param bat_pin: The pin used to sense battery voltage.
    :param bat_capacity: The battery capacity, in mAh.
    """
    def __init__(self, bat_pin='P16', bat_capacity=1000):
        self.bat_capacity = bat_capacity

        #Configure ADC for battery voltage sensing
        adc = ADC()
        #Configure 2.5dB attenuator to be able to capture full range of battery
        #voltages
        self.bat_adc = adc.channel(pin=bat_pin, attn=ADC.ATTN_2_5DB)

        #Battery voltage is sensed through a voltage divider with
        #115kOhm and 56kOhm, such that V_ADC = V_batt * 56/(115+56)
        self.a = 171.0/56.0

    def bat_pin_voltage(self):
        """Makes 100 voltage measurements of bat_pin, then converts
        ADC values to actual voltages.
        """

        #100 voltage measurements
        sum=0
        for i in range(0,100):
            sum+=self.bat_adc()

        adc_val = int(round(sum/100.0))

        #LoPy ADC linearity window begins at 60 and ends at 4000
        if(adc_val < 60):
            return 0.0
        #At ATTN_2_4_DB 4000 corresponds to approx. 1.32V
        if(adc_val > 4000):
            return 1.32

        #These values were experimentally determined
        a = 3273
        b = -303

        return (adc_val - b)/a

    def voltage(self):
        """Return the battery voltage."""

        return self.a * self.bat_pin_voltage()

    def soc(self):
        """Return the approximated state of charge, in percent.
        Caution: does not work when USB power is present (i.e.: while charging).

        This approximation is based on a piece-wise linear approximation of a
        typical Li-Po battery discharge curve.
        """
        a = 0.0
        b= 0.0

        if(self.voltage() <= 3.27):
            a = 0.0
            b= 0.0
        elif(self.voltage() <= 3.6):
            a = 50.0
            b = -175.0
        elif(self.voltage() <= 3.87):
            a = 294.12
            b = -1078.24
        elif(self.voltage() <= 4.2):
            a = 121.21
            b = -409.09
        else:
            a = 0.0
            b = 100.0

        return a*self.voltage() + b

    def energy(self):
        """Return an approximate of the energy available in the battery (in J).
        Caution: does not work when USB power is present (i.e.: while charging).
        """

        #Multiplying the battery state of charge by its capacity at full charge
        #gives the battery capacity at the time of measrement (in mAh).
        #Multiplying this capacity by the measured voltage gives how much
        #energy is left in the battery (in mWh).
        E_mWh = self.bat_capacity * self.soc() * self.voltage()

        #1mWh = 10^(-3)J.s^(-1).h = 3600*10^(-3)J.s^(-1).s = 3.6J
        return 3.6*E_mWh

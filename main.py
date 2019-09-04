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

import binascii
import socket
import time

import cbor
import pycom
from network import LoRa

import monitor

# Hyper Parameters
debug = True
rounds = 10  # Running rounds for the collect and send loop
# LoRA message type may be confirmable or not-confirmable
message_type = True
data_rate = 5  # Data rate of the lora connection
data_send_timeout = 10
# Power mode may be LoRa.ALWAYS_ON, LoRa.TX_ONLY or LoRa.SLEEP
lora_mode = LoRa.SLEEP
delay = 1  # Loop collect/send message delay (in secs)

# Credentials for IMT Server
app_eui = b'\x48\x62\x66\x27\x56\x63\x68\x53'
app_key = binascii.unhexlify(
    '11 22 33 44 55 66 77 88 11 22 33 44 55 66 77 88'.replace(' ', ''))


def join_lora_gw(l_conn):
    """
    Procedure to create the socket to the LoRA gateway.
    :param l_conn: the lora connectionn obejct
    :return: the socket just created
    """
    # Join the network (or re-join if connection lost)
    l_conn.join(activation=LoRa.OTAA,
                auth=(app_eui, app_key), timeout=0)
    # Initialize LoRaWAN socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    # Configuring data rate (between 0 and 5)
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, data_rate)
    # Selecting non-confirmed type of messages
    s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, message_type)

    return s


def check_connection(l_conn):
    """
    Check on the connection with the gateway and switch on or off the on-board
    LED acconrdingly
    :param l_conn:
    :return:
    """
    while not l_conn.has_joined():
        pycom.rgbled(0x43142f)  # LED Violet
    pycom.rgbled(0x000000)  # LED OFF


def send_lora_gw(l_conn, s, d):
    """
    Procedure to send any well-formed dictionary to the LoRA gateway
    :param l_conn: the lora connection object
    :param s: the socket object
    :param d: the dictionary to be converted into CBOR data format
    :return:
    """
    if debug:
        print('Waiting for a LoRa connection...')
        check_connection(l_conn)
        print('Connected.')

    # Convert the dictionary message into CBOR
    msg = cbor.dumps(d)
    if debug:
        print('Message content: ' + str(msg) +
              ' (length is ' + str(len(msg)) + ' bytes).')

    # Wait until data is sent (max. 10s)
    s.setblocking(True)
    s.settimeout(data_send_timeout)

    if debug:
        print('Sending message...')
    pycom.rgbled(0x00007f)  # LED Blue
    try:
        s.send(msg)
    except:
        if debug:
            print('Failed to send message!')

    s.setblocking(False)
    if debug:
        print('Message sent!')
    pycom.rgbled(0x000000)  # LED OFF

    return s.recv(64)


def build_data_dict():
    res_temp_humidity = monitor.get_temp_humidity()
    res_gps = monitor.get_gps()
    res_pm10_pm25 = monitor.get_pm10_pm25()
    res_co2_tvoc = monitor.co2_tvoc()
    return {
        # get me the current time
        "ts": time.ticks_ms(),
        # get me location
        "x": res_gps[0] if res_gps is not None else 0,
        "y": res_gps[1] if res_gps is not None else 0,
        "z": res_gps[2] if res_gps is not None else 0,
        # get me raw data
        "tm": res_temp_humidity[0] if res_temp_humidity is not None else 0,
        "hm": res_temp_humidity[1] if res_temp_humidity is not None else 0,
        "p1": res_pm10_pm25[0] if res_pm10_pm25 is not None else 0,
        "p2": res_pm10_pm25[1] if res_pm10_pm25 is not None else 0,
        "co": res_co2_tvoc[0] if res_co2_tvoc is not None else 0,
        "tv": res_co2_tvoc[1] if res_co2_tvoc is not None else 0
    }


if __name__ == '__main__':
    # Initialize LoRa
    lora_connection = LoRa(mode=LoRa.LORAWAN)
    lora_connection.power_mode(lora_mode)
    soc = join_lora_gw(lora_connection)

    # Collect and Send data
    i = 0
    while i < rounds:
        data_dict = build_data_dict()
        ack = send_lora_gw(lora_connection, soc, data_dict)
        if debug:
            print('Received:' + str(ack) + '\n')
        time.sleep(delay)
        i += 1

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
from network import LoRa

import pycom_monitor

# Hyper Parameters
debug = True

# delay times -- different for every sensors group
delay_am2320_sgp30 = 5  # temp and gas take more frequent measures
delay_gps = 10
delay_sds011 = 30  # fan sensor delay should be multiple of 30
delay_ssd1306 = 120  # just for log purpose on the monitor

# LoRa specific parameters
message_type = True  # LoRA confirmable message True or False
data_rate = 5  # Data rate of the lora connection
data_send_timeout = 10
lora_mode = LoRa.SLEEP  # Power mode LoRa.ALWAYS_ON, LoRa.TX_ONLY or LoRa.SLEEP

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


def send_lora_gw(l_conn, s, d):
    """
    Procedure to send any well-formed dictionary to the LoRA gateway
    :param l_conn: the lora connection object
    :param s: the socket object
    :param d: the dictionary to be converted into CBOR data format
    :return:
    """

    if d == {}:
        return None

    # Check the connection status before to send
    if debug:
        print('Waiting for a LoRa connection...')
        while not l_conn.has_joined():
            time.sleep(1)
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
    try:
        s.send(msg)
        s.setblocking(False)
        if debug:
            print('Message sent!')
    except Exception:
        if debug:
            print('Failed to send message!')

    rec = None
    try:
        rec = s.recv(64)
    except TimeoutError:
        if debug:
            print(d)
            print("ack has not been received")

    return rec


def build_data_dict(labels, am2320_res = None, sgp30_res = None, gps_res = None,
                    sds011_res = None):
    """
    Produce a dictionary of measurements from the board sensors
    :param labels:
    :param am2320_res:
    :param sgp30_res:
    :param gps_res:
    :param sds011_res:
    :return:
    """
    data = {}
    if am2320_res is not None:
        data[labels["temperature"]] = am2320_res[0]
        data[labels["humidity"]] = am2320_res[1]
    if sgp30_res is not None:
        data[labels["co2"]] = sgp30_res[0]
        data[labels["tvoc"]] = sgp30_res[1]
    if gps_res is not None:
        data[labels["gps_longitude"]] = gps_res[0]
        data[labels["gps_latitude"]] = gps_res[1]
        data[labels["gps_altitude"]] = gps_res[2]
    if sds011_res is not None:
        data[labels["dust_pm10"]] = sds011_res[0]
        data[labels["dust_pm25"]] = sds011_res[1]

    return data


if __name__ == '__main__':
    # Initialize LoRa
    lora_connection = LoRa(mode=LoRa.LORAWAN)
    lora_connection.power_mode(lora_mode)
    soc = join_lora_gw(lora_connection)

    # Launch the collect and send data loop
    t = 0
    am2320, sgp30, gps, sds011 = None, None, None, None
    while True:
        time.sleep(1)
        t += 1
        if t % delay_am2320_sgp30 == 0:
            am2320 = pycom_monitor.temperature_humidity(n_try_max=10)
            sgp30 = pycom_monitor.co2_tvoc()
        if t % delay_gps == 0:
            gps = pycom_monitor.latitude_longitude_altitude(update_rate=1000)
        if t % delay_sds011 - 30 == 0:
            sds011_ok = pycom_monitor.bootstrap_pm10_pm25()
        if t % delay_sds011 == 0 and sds011_ok:
            sds011 = pycom_monitor.read_pm10_pm25()
        if t % delay_ssd1306 == 0:
            pycom_monitor.print_lcd(time.ctime(time.time()))

        ack = send_lora_gw(
            lora_connection,
            soc,
            build_data_dict({
                "timestamp": "ts",
                "temperature": "tm",
                "humidity": "hu",
                "co2": "c",
                "tvoc": "tv",
                "gps_longitude": "x",
                "gps_latitude": "y",
                "gps_altitude": "z",
                "dust_pm10": "pm10",
                "dust_pm25": "pm25"
            },
                am2320,
                sgp30,
                gps,
                sds011))

        if debug and ack is not None:
            print('Received:' + str(ack) + '\n')

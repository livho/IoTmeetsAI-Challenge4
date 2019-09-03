from network import LoRa
import binascii
import cbor
import pycom
import socket
import time

###Initialize LoRa###
lora = LoRa(mode=LoRa.LORAWAN)

#Power mode may be LoRa.ALWAYS_ON, LoRa.TX_ONLY or LoRa.SLEEP.
lora.power_mode(LoRa.TX_ONLY)

#Credentials
app_eui = b'\x48\x62\x66\x27\x56\x63\x68\x53'
app_key = binascii.unhexlify('11 22 33 44 55 66 77 88 11 22 33 44 55 66 77 88'.replace(' ',''))

#Join the network (or re-join if connection lost)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

#Initialize LoRaWAN socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
#Configuring data rate (between 0 and 5)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)
#Selecting non-confirmed type of messages
s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, False)

while True:
    #Wait for Lora connection
    print('Waiting for a LoRa connection...')
    while not lora.has_joined():
        pycom.rgbled(0x43142f) #LED Violet
    print('Connected.')
    pycom.rgbled(0x000000) #LED OFF

    #Prepare message
    msg = 'Hello, world!'
    #Convert to CBOR
    msg = cbor.dumps(msg)

    print('Message content: ' + str(msg) + ' (length is ' + str(len(msg)) + ' bytes).')

    #Wait until data is sent (max. 10s)
    s.setblocking(True)
    s.settimeout(10)

    print('Sending message...')
    pycom.rgbled(0x00007f) #LED Blue
    try:
        s.send(msg)
    except:
        print('Failed to send message!')

    s.setblocking(False)
    print('Message sent!')
    pycom.rgbled(0x000000) #LED OFF

    data = s.recv(64)
    print('Received:' + str(data) + '\n')

    time.sleep(10)

from network import LoRa
import binascii
import cbor
import pycom
import socket
import time

debug = True

###Hyper Parameters###
rounds = 10  # Running rounds for the collect and send loop
# LoRA message may be confirmable or not-confirmable, receive ot not a confirmation message
message_type = True
data_rate = 5  # Data rate of the lora connection
data_send_timeout = 10
# Power mode may be LoRa.ALWAYS_ON, LoRa.TX_ONLY or LoRa.SLEEP.
lora_mode = LoRa.TX_ONLY
delay = 1  # Loop collect/send message delay (in secs)

# Credentials for IMT Server
app_eui = b'\x48\x62\x66\x27\x56\x63\x68\x53'
app_key = binascii.unhexlify(
    '11 22 33 44 55 66 77 88 11 22 33 44 55 66 77 88'.replace(' ', ''))


def join_lora_gw(lora_connection):
    """
    Procedure to create the socket to the LoRA gateway.
    @param l the lora connectionn obejct
    @return the socket just created
    """
    # Join the network (or re-join if connection lost)
    lora_connection.join(activation=LoRa.OTAA,
                         auth=(app_eui, app_key), timeout=0)
    # Initialize LoRaWAN socket
    soc = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    # Configuring data rate (between 0 and 5)
    soc.setsockopt(socket.SOL_LORA, socket.SO_DR, data_rate)
    # Selecting non-confirmed type of messages
    soc.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, message_type)

    return soc


def check_connection(lora_connection):
    """
    Check on the connection with the gateway and switch on or off the on-board LED acconrdingly
    @param lora_connection the lora connection object
    @return bool whetear the connection is still on or not
    """
    if debug:
        print('Waiting for a LoRa connection...')
    while not lora_connection.has_joined():
        pycom.rgbled(0x43142f)  # LED Violet
    if debug:
        print('Connected.')
    pycom.rgbled(0x000000)  # LED OFF


def send_lora_gw(lora_connection, soc, d):
    '''
    Procedure to send any well-formed dictionary to the LoRA gateway
    @param lora_connection the lora connection object
    @param soc the socket object
    @param d the dictionary to be converted into CBOR data format
    '''
    #check_connection(lora_connection)

    # Convert the dictionary message into CBOR
    msg = cbor.dumps(d)
    if debug:
        print('Message content: ' + str(msg) +
              ' (length is ' + str(len(msg)) + ' bytes).')

    # Wait until data is sent (max. 10s)
    soc.setblocking(True)
    soc.settimeout(data_send_timeout)

    if debug:
        print('Sending message...')
    pycom.rgbled(0x00007f)  # LED Blue
    try:
        soc.send(msg)
    except:
        if debug:
            print('Failed to send message!')

    soc.setblocking(False)
    if debug:
        print('Message sent!')
    pycom.rgbled(0x000000)  # LED OFF

    return soc.recv(64)

def build_data_dict():
    return {
        "a": 23.0
    }

if __name__ == '__main__':
    """
    Send data gathered from a PyCom board to a LoRA endpoint
    """
    ###Initialize LoRa###
    lora_connection = LoRa(mode=LoRa.LORAWAN)
    lora_connection.power_mode(lora_mode)
    soc = join_lora_gw(lora_connection)

    ###Collect and Send data###
    i = 0
    while i < rounds:
        data_dict = build_data_dict()
        ack = send_lora_gw(lora_connection, soc, data_dict)
        if debug:
            print('Received:' + str(ack) + '\n')
        time.sleep(delay)
        i += 1

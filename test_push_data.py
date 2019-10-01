import socket
import time
import random

HOST ="127.0.0.1"
PORT =80

def connectSocket():
    while True:
        try:
            print("Attempting to Connect.")
            skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skt.settimeout(2)
            skt.connect((HOST,PORT))
            return skt
        except socket.error:
            print("Unable to Connect: Retrying in 2 seconds.")
            time.sleep(2)

skt = connectSocket()
while True:
    try:
        ser_str = "{0}\t{1}".format(random.randrange(5000, 6000), random.randrange(5000, 6000))
        print("Sending: " + ser_str)
        skt.send(ser_str.encode('utf-8'))
        time.sleep(.2)
    except socket.error as e:
        print("Lost Connection!")
        skt = connectSocket()
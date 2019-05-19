import socket
import serial
import time


HOST ="192.168.1.98"
PORT =8000

#Serial setup
ser = serial.Serial('/dev/ttyACM0',9600)

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
        ser_str = str(ser.readline())
        print("Sending: " + ser_str)
        skt.send(ser_str.encode('utf-8'))
        time.sleep(1)
    except socket.error as e:
        print("Lost Connection!")
        skt = connectSocket()
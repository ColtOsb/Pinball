import curses
import os
import time
import keyboard
from pymodbus.client import ModbusTcpClient
# Address 11 is left flipper read, 12 is right flipper read
# Address 13 is left flipper write, 14 is right flipper write
# Address 3 is autokicker

class PLCConnection:
        
    def __init__(self,ip_address="192.168.1.10",port_number=502):
        self.ip_address = ip_address
        self.port_number = port_number

    def activateAutoKick(self):
        self.client.write_coil(3,[True])

    def activateLeft(self):
        self.client.write_coil(13,[True])

    def activateRight(self):
        self.client.write_coil(14,True)

    def deactivateLeft(self):
        self.client.write_coil(13,False)

    def deactivateRight(self):
        self.client.write_coil(14,False)

    def connectToPlc(self):
        self.client = ModbusTcpClient(self.ip_address,port=self.port_number)
        if self.client.connect():
            return True
        else:
            self.client = None
            return False

if __name__ == "__main__":
    def main(win,client):
        key = ""
        leftActive = False
        rightActive = False
        while True:
            try:
                key = win.getkey()
                win.clear()
                win.addstr("Detected Key:")
                win.addstr(f"{key}")
                if(key == "KEY_LEFT" or key == "a"):
                    if not leftActive:
                        client.activateLeft()
                        leftActive = True
                    else:
                        client.deactivateLeft()
                        leftActive = False
                elif(key == "KEY_RIGHT" or key == "d"):
                    if not rightActive:
                        client.activateRight()
                        rightActive = True
                    else:
                        client.deactivateRight()
                        rightActive = False
                elif(key == "KEY_UP"):
                    client.deactivateLeft()
                    leftActive = False
                    rightActive = False
                    client.deactivateRight()
                elif(key == " "):
                    client.activateAutoKick()
                elif(key == "q" or key == os.linesep):
                    break
            except:
                pass
    client = PLCConnection()
    if(client.connectToPlc()):
        try:
            curses.wrapper(main,client)
        finally:
            client.client.close()

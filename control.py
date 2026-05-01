from pymodbus.client import ModbusTcpClient
# Address 11 is left flipper read, 12 is right flipper read
# Address 13 is left flipper write, 14 is right flipper write
# Address 3 is autokicker

# Address 6 is ball drain

class PLCConnection:

    input_registers = {
        "BALL_DRAIN": 6,
        "GAME_ACTIVE": 4,
    }

    output_registers = {
        "AUTOKICK": 3,
        "FLIPPER_LEFT": 13,
        "FLIPPER_RIGHT": 14,
        "START_GAME": 15,
    }
        
    def __init__(self,ip_address="192.168.1.10", port_number=502, connect=False):
        self.ip_address = ip_address
        self.port_number = port_number
        self.ballDrain = None
        if connect:
            self.ConnectToPLC


    def ActivateAutoKick(self):
        self.client.write_coil(PLCConnection.output_registers["AUTOKICK"],[True])


    def ActivateLeft(self):
        self.client.write_coil(PLCConnection.output_registers["FLIPPER_LEFT"],[True])


    def ActivateRight(self):
        self.client.write_coil(PLCConnection.output_registers["FLIPPER_RIGHT"],[True])


    def DeactivateLeft(self):
        self.client.write_coil(PLCConnection.output_registers["FLIPPER_LEFT"],[False])


    def DeactivateRight(self):
        self.client.write_coil(PLCConnection.output_registers["FLIPPER_RIGHT"],[False])


    def ReadBallDrain(self):
        ballDrain = self.client.read_input_registers(address=PLCConnection.input_registers["BALL_DRAIN"],count=1)
        if self.ballDrain is None:
            self.ballDrain = ballDrain.registers[0]
            
        if self.ballDrain == ballDrain.registers[0]:
            return (False,self.ballDrain)
        else:
            self.ballDrain = ballDrain.registers[0]
            return (True,self.ballDrain)


    def StartGame(self):
        self.client.write_coil(PLCConnection.output_registers["START_GAME"],True)


    def GameActive(self):
        start = self.client.read_coils(address=PLCConnection.input_registers["GAME_ACTIVE"],count=1)
        return start.bits[0]


    def ConnectToPLC(self):
        self.client = ModbusTcpClient(self.ip_address,port=self.port_number)
        if not self.client.connect():
            self.client = None
            raise Exception(f"ERROR: UNABLE TO ESTABLISH CONNECTION TO PLC HOST {self.ip_address}:{self.port_number}")


    def Disconnect(self):
        if self.client:
            self.client.close()


if __name__ == "__main__":
    import curses
    import os
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
                if (key == "s"):
                    client.startGame()
                if(key == "KEY_LEFT" or key == "a"):
                    if not leftActive:
                        client.ActivateLeft()
                        leftActive = True
                    else:
                        client.DeactivateLeft()
                        leftActive = False
                elif(key == "KEY_RIGHT" or key == "d"):
                    if not rightActive:
                        client.ActivateRight()
                        rightActive = True
                    else:
                        client.DeactivateRight()
                        rightActive = False
                elif(key == "KEY_UP"):
                    client.DeactivateLeft()
                    leftActive = False
                    rightActive = False
                    client.DeactivateRight()
                elif(key == " "):
                    client.ActivateAutoKick()
                elif(key == "q" or key == os.linesep):
                    break
            except:
                pass
    client = PLCConnection()
    if(client.connectToPlc()):
        try:
            curses.wrapper(main,client)
        finally:
            client.Disconnect()

from enum import Enum
from datetime import datetime
class Flipper:
    sides = Enum("sides",[("LEFT",1),("RIGHT",2)])

    def __init__(self,side):
        self.active = False
        self.last_modified = 0
        self.side = side

    def Activate(self,plc_client):
        # Does nothing if already active
        if self.active:
            return 1

        # Determines which flipper to activate
        if self.side == Flipper.sides.LEFT:
            plc_client.activateLeft()
        elif self.side == Flipper.sides.RIGHT:
            plc_client.activateRight()

        # Invalid side set
        else:
            return 2

        # Housekeeping variables
        self.active = True
        self.last_modified = datetime.now().timestamp()
        return 0
        

    def Deactivate(self,plc_client):
        # Does nothing if not already active
        if not self.active:
            return 1

        # Determines which flipper to activate
        if self.side == Flipper.sides.LEFT:
            plc_client.deactivateLeft()
        elif self.side == Flipper.sides.RIGHT:
            plc_client.deactivateRight()

        # Invalide side set
        else:
            return 2

        # Housekeeping variables
        self.active = False
        self.last_modified = datetime.now().timestamp()
        return 0

    def Toggle(self,plc_client,value=None):
        if value is not None:
            self.Deactivate(plc_client) if self.active else self.Activate(plc_client)
        else:
            self.Activate(plc_client) if value else self.Deactivate(plc_client)

    def __str__(self):
        return f"Flipper: {self.side} Status: {'Active' if self.active else 'Inactive'}"

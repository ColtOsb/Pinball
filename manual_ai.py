#! /usr/bin/env python3
import cv2
import numpy as np
from control import PLCConnection
from perspective import Perspective
import vision
from vision import Circles
from datetime import datetime
from config import AI as ai_config
import VideoCapture
import json
from enum import Enum
import time

class State(Enum):
    CRADLE_LEFT = 0
    CRADLE_RIGHT = 1
    DRAIN_CENTER = 2
    DRAIN_LEFT = 3
    DRAIN_RIGHT = 4
    NEARBY = 5
    OTHER = 6
    INACTIVE = 7


class Flipper:
    sides = Enum("sides",[("LEFT",1),("RIGHT",2)])

    def __init__(self,side):
        self.active = False
        self.last_activated = 0
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
        self.last_activated = datetime.now().timestamp()
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
        self.last_activated = 0
        return 0

    def Toggle(self,plc_client,value=None):
        if value is not None:
            self.Deactivate(plc_client) if self.active else self.Activate(plc_client)
        else:
            self.Activate(plc_client) if value else self.Deactivate(plc_client)

def LoadStateBounds(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
        try:
            data = data[0]["states"]
            return data
        except (IndexError, KeyError):
            return None
    except FileNotFoundError:
        return None

def HandleStateInactive(plc_client,game_stats,kicker_cooldown):
    if game_stats["balls"] < 3:
        time.sleep(kicker_cooldown)
        plc_client.activateAutoKick()
        game_stats["balls"] += 1
        return (State.OTHER, 0)
    return (State.INACTIVE,1)



if __name__ == "__main__":

    # Stores the state and status of each flipper
    flippers = {
            "left": Flipper(Flipper.sides.LEFT),
            "right": Flipper(Flipper.sides.RIGHT),
            }

    # Initializes ball location state
    current_state = State.INACTIVE
    state_bounds_filepath = "states.json"
    state_bounds = LoadStateBounds(state_bounds_filepath)
    if not state_bounds:
        print(f"ERROR: INVALID STATE BOUNDS JSON FILE OR INCORRECT PATH ({state_bounds_filepath}).",flush=True)
        exit(1)

    # Connect to PLC
    client = PLCConnection()
    if not client.connectToPlc():
        print("ERROR: UNABLE TO ESTABLISH CONNECTION TO PLC.",flush=True)
        exit(1)

    games_to_play = 1
    games_completed = 0

    # Successfully connected to PLC
    try:

        # Initial setup before gameplay loop
        cam = VideoCapture.VideoCapture(0)
        perspective = Perspective()

        # Loop for complete games
        while games_completed < games_to_play:

            # Start Game and kick ball
            client.startGame()
            game_stats = {
                    "balls": 0
                    }
            current_game = games_completed

            # Gameplay loop involving analyzing each frame
            while current_game == games_completed:

                # Reads frame and performs necessary transformations
                frame = cam.read()
                processed_frame = vision.PreprocessFrame(frame,perspective,ai_config.y_minimum,ai_config.y_maximum,ai_config.x_right_minimum,ai_config.x_left_maximum,for_cnn=False)
                circles = Circles.detectCircles(processed_frame)
                display_frame = circles.displayCircles(circles,processed_frame)

                # Gets coordinate of ball
                ball_location = Circles.locateCircles(circles)


                # Logic deciding what to do
                match current_state:
                    case State.CRADLE_LEFT:
                        pass
                    case State.Cradle_RIGHT:
                        pass
                    case State.Drain_CENTER:
                        pass
                    case State.DRAIN_LEFT:
                        pass
                    case State.DRAIN_RIGHT:
                        pass
                    case State.OTHER:
                        pass
                    case State.NEARBY:
                        pass

                    # No ball in play
                    case State.Inactive:
                        current_state, status = HandleStateInactive(client,game_stats,ai_config.kickerCooldown)

                        # Max number of balls for game have been dispensed
                        if status:
                            games_completed += 1
                            continue
                    case _:
                        raise ValueError(f"INVALID STATE: {current_state}")

                cv2.imshow('Machine Vision', display_frame)

                # Check if a ball was drained
                ball_drained, balls_left = client.readBallDrain()
                if ball_drained:

                    # More than 0 balls left in game
                    if balls_left > 0:
                        current_state = State.INACTIVE
                        print("Ball Drained")

                    # No balls left in game
                    else:
                        games_completed += 1
                        current_state = State.INACTIVE
                        print(f"End of game {games_completed} out of {games_to_play}.")


                if cv2.waitKey(1) == ord('q'):
                    break
            #cam.release()
            cv2.destroyAllWindows()
                            
    finally:
        client.client.close()

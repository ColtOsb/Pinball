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
import polygon

class State(Enum):
    CRADLE_LEFT = 0
    CRADLE_RIGHT = 1
    DRAIN_CENTER = 2
    DRAIN_LEFT = 3
    DRAIN_RIGHT = 4
    NEARBY = 5
    OTHER = 6
    INACTIVE = 7
    KILL = 8


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

def CreateStateBoundShapes(data):
    for i in data.keys():
        state = data[i]
        for zone in [x for x in state.keys() if "zone" in x]:
            points = [polygon.Point(x[0],x[1]) for x in state[zone]]
            for p in points:
                print(p,end=",")
            print("")
            poly = polygon.Polygon(points)
            print(poly)
            data[i][zone] = poly
    return data

def LoadStateBounds(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
        try:
            data = data[0]
            print(data)
            data = CreateStateBoundShapes(data)
            return data
        except (IndexError, KeyError):
            return None
    except FileNotFoundError:
        return None

def HandleStateCradleLeft(plc_client, flippers, ball_location, state_bounds):
    flippers["left"].Activate(plc_client)
    if ball_location:
        if state_bounds["CRADLE_LEFT"]["holding_zone"].DoesPointIntersect(x=ball_location[0],y=ball_location[1]):
            print ("BALL IN HOLDING ZONE")
            flippers["left"].Deactivate(plc_client)
            return (State.OTHER,0)
    return (State.CRADLE_LEFT,0)


def HandleStateOther(plc_client, ball_location, state_bounds):
    if ball_location:
        # Check if should enter CRADLE_LEFT state
        if state_bounds["CRADLE_LEFT"]["entry_channel_zone"].DoesPointIntersect(x=ball_location[0],y=ball_location[1]):
            print ("ENTER CRADLE LEFT")
            return (State.CRADLE_LEFT,0)
    return (State.OTHER,0)

def HandleStateInactive(plc_client,game_stats,kicker_cooldown):
    if game_stats["balls"] < 3:
        time.sleep(2*kicker_cooldown)
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
    #exit(0)
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
            if current_state == State.KILL:
                break

            # Start Game and kick ball
            print("Starting game")
            client.startGame()
            current_state = State.INACTIVE
            game_stats = {
                    "balls": 0,
                    "balls_per_game": 3
                    }
            current_game = games_completed
            print(f"current game {current_game}. Completed {games_completed}")

            # Gameplay loop involving analyzing each frame
            while current_game == games_completed:

                # Reads frame and performs necessary transformations
                frame = cam.read()
                processed_frame = vision.PreprocessFrame(frame,perspective,ai_config.y_minimum,ai_config.y_maximum,ai_config.x_right_minimum,ai_config.x_left_maximum,for_cnn=False)
                circles = Circles.detectCircles(processed_frame)
                display_frame = Circles.displayCircles(circles,processed_frame)

                # Gets coordinate of ball
                ball_location = Circles.locateCircles(circles)


                # Logic deciding what to do
                match current_state:
                    case State.CRADLE_LEFT:
                        current_state, status = HandleStateCradleLeft(client, flippers, ball_location, state_bounds)
                    case State.CRADLE_RIGHT:
                        pass
                    case State.DRAIN_CENTER:
                        pass
                    case State.DRAIN_LEFT:
                        pass
                    case State.DRAIN_RIGHT:
                        pass
                    case State.OTHER:
                        current_state, status = HandleStateOther(client,ball_location, state_bounds)
                    case State.NEARBY:
                        pass

                    # No ball in play
                    case State.INACTIVE:
                        current_state, status = HandleStateInactive(client,game_stats,ai_config.kickerCooldown)

                        # Max number of balls for game have been dispensed
                        if status:
                            games_completed += 1
                            continue
                    case _:
                        print("BAD STATE")
                        raise ValueError(f"INVALID STATE: {current_state}")

                cv2.imshow('Machine Vision', display_frame)

                # Check if a ball was drained
                ball_drained, num_balls_drained = client.readBallDrain()
                if ball_drained and num_balls_drained > 0:

                    current_state = State.INACTIVE
                    print(f"Ball: {num_balls_drained} drained")

                    # No balls left in game
                    if num_balls_drained >= game_stats["balls_per_game"]:
                        games_completed += 1
                        print(f"End of game {games_completed} out of {games_to_play}.")
                        time.sleep(3)


                if cv2.waitKey(1) == ord('q'):
                    current_state = State.KILL
                    break

        print("End of all games. Exiting...")
        #cam.release()
        cv2.destroyAllWindows()
                            
    finally:
        print("Closing client")
        client.client.close()
        print("Client closed")

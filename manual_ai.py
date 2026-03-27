#! /usr/bin/env python3
import cv2
import numpy as np
from control import PLCConnection
from perspective import Perspective
from vision import Circles
from datetime import datetime
from config import AI as ai_config
from copy import copy
import math
import predict
import VideoCapture
#Centimeter = 5.3 px
import json
from enum import Enum

class State(Enum):
    CRADLE_LEFT = 0
    CRADLE_RIGHT = 1
    DRAIN_CENTER = 2
    DRAIN_LEFT = 3
    DRAIN_RIGHT = 4
    NEARBY = 5
    OTHER = 6
    INACTIVE = 7


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



if __name__ == "__main__":

    # Stores the state and status of each flipper
    flippers = {
            "left": {
                "active": False,
                "last_activated": 0
                },
            "right": {
                "active": False,
                "last_activated": 0
                }
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

    # Successfully connected to PLC
    try:

        # Initial setup before gameplay loop
        drainTime = 0
        kickCount = 0
        gameCount = 0
        roundEndTime = 0
        firstKickTimer = 0
        firstKickComplete = False
        print(f"Tick frequency: {cv2.getTickFrequency()}")
        cam = VideoCapture.VideoCapture(0)
        perspective = Perspective()
        client.startGame()
        gameCount += 1
        count = 0

        # Gameplay loop involving analyzing each frame
        while True:

            # Reads frame and performs necessary transformations
            frame = cam.read()
            frame = perspective.applyPerspectiveTransform(frame)
            cropped_frame = frame[ai_config.y_minimum:ai_config.y_maximum, ai_config.x_right_minimum: ai_config.x_left_maximum].copy()
            gray = Circles.prep(cropped_frame)
            # Probably need to add something to get ball location as a coordinate
            # And remove everything related to CNN
            img = cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
            img = cv2.resize(img,(290,135))
            img = img.astype('float32') / 255.0
            img = np.expand_dims(img,axis=0)

            # Activates auto kicker
            if not firstKickComplete:
                if not firstKickTimer:
                    firstKickTimer = datetime.now().timestamp()
                elif datetime.now().timestamp() >= firstKickTimer + ai_config.kickerCooldown:
                    client.activateAutoKick()
                    firstKickComplete = True

            # Logic deciding what to do
            match prediction:
                case 2: 
                    if not leftActive and datetime.now().timestamp() > leftActivated+ai_config.flipper_cooldown:
                        client.activateLeft()
                        leftActive = True
                        leftActivated = datetime.now().timestamp()
                        print("left flipper",leftActivated)
                case 3:
                    if not rightActive and datetime.now().timestamp() > rightActivated+ai_config.flipper_cooldown:
                        client.activateRight()
                        rightActive = True
                        rightActivated = datetime.now().timestamp()
                        print("right flipper",rightActivated)
                case _:
                    print('no action')
            if leftActive and datetime.now().timestamp() >= leftActivated+ai_config.flipper_timeout:
                client.deactivateLeft()
                leftActive = False
                leftActivated = datetime.now().timestamp()
                print("Deactivate Left Flipper")

            if rightActive and datetime.now().timestamp() >= rightActivated+ai_config.flipper_timeout:
                client.deactivateRight()
                rightActive = False
                rightActivated = datetime.now().timestamp()
                print("Deactivate Right Flipper")
            """
            if location[0] >= 0 and location [1] >= 0:
                print(location)
            x = location[0] + ai_config.x_right_minimum
            y = location[1] + ai_config.y_minimum
            if y >= ai_config.y_minimum and y < ai_config.y_maximum:
                if x >= ai_config.x_left_minimum and x < ai_config.x_left_maximum:
                    if not leftActive and datetime.now().timestamp() > leftActivated+ai_config.flipper_cooldown:
                        client.activateLeft()
                        leftActive = True
                        leftActivated = datetime.now().timestamp()
                        print("left flipper",leftActivated)
                if x >= ai_config.x_right_minimum and x < ai_config.x_right_maximum:
                    if not rightActive and datetime.now().timestamp() > rightActivated+ai_config.flipper_cooldown:
                        client.activateRight()
                        rightActive = True
                        rightActivated = datetime.now().timestamp()
                        print("right flipper",rightActivated)
            if leftActive and datetime.now().timestamp() >= leftActivated+ai_config.flipper_timeout:
                client.deactivateLeft()
                leftActive = False
                leftActivated = datetime.now().timestamp()
                print("Deactivate Left Flipper")

            if rightActive and datetime.now().timestamp() >= rightActivated+ai_config.flipper_timeout:
                client.deactivateRight()
                rightActive = False
                rightActivated = datetime.now().timestamp()
                print("Deactivate Right Flipper")
            """
            #Circles.displayCircles(circles,frame,offset=(ai_config.x_right_minimum,ai_config.y_minimum))
            cv2.rectangle(frame,(400,28),(525,175),255,3)
            cv2.rectangle(frame,(235,28),(360,175),255,3)
            cv2.imshow('Machine Vision', gray)
            ball_drain = client.readBallDrain()
            if ball_drain[0]:
                if ball_drain[1] > 0:
                    print("Ball Drained")
                    drainTime = datetime.now().timestamp()
                else:
                    print("Game {0} of {1} Complete".format(gameCount, ai_config.numRounds))
                    roundEndTime = datetime.now().timestamp()
                    passiveState = True

            if ball_drain[1] > 0 and datetime.now().timestamp() >= drainTime + ai_config.kickerCooldown and ball_drain[1] > kickCount:
                client.activateAutoKick()
                kickCount += 1
                print("Launching Ball")
            if passiveState == True and ball_drain[1] == 0 and datetime.now().timestamp() >= roundEndTime + ai_config.roundTimer and gameCount is not ai_config.numRounds:
                client.startGame()
                kickCount = 0
                gameCount += 1
                passiveState = False
                firstKickTimer = 0
                firstKickComplete = False

            if cv2.waitKey(1) == ord('q'):
                break
        #cam.release()
        cv2.destroyAllWindows()
        for key,x in execution_times.items():
            total = 0
            for y in x:
                total += (y[1] - y[0]) / cv2.getTickFrequency()
                
    finally:
        client.client.close()

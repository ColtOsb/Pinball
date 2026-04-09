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
import keras
#Centimeter = 5.3 px
from enum import Enum
from flipper import Flipper
import time

class State(Enum):
    KILL = 0
    INACTIVE = 1
    OUT_OF_PLAY = 2
    IN_PLAY = 3


def UseFlipperLogic(flipper: Flipper, enable_output: bool = False):
    if not flipper.active and datetime.now().timestamp() > flipper.last_modified + ai_config.flipper_cooldown:
        flipper.Activate(client)
    if enable_output:
        print(flipper)


if __name__ == "__main__":
    model = predict.loadModel()
    client = PLCConnection()
    current_state = State.OUT_OF_PLAY

    if not client.connectToPlc():
        print("ERROR: UNABLE TO ESTABLISH CONNECTION TO PLC.",flush=True)
        exit(1)

    games_to_play = ai_config.numRounds
    games_completed = 0
    flippers = {
        "left": Flipper(Flipper.sides.LEFT),
        "right": Flipper(Flipper.sides.RIGHT),
    }

    try:
        cam = VideoCapture.VideoCapture(0)
        perspective = Perspective()
        while games_completed < games_to_play:
            if current_state == State.KILL:
                break
            # Start Game and kick ball
            print("Starting game")
            client.startGame()
            current_state = State.INACTIVE
            current_game = games_completed
            print(f"current game {current_game}. Completed {games_completed}")

            # Gameplay loop involving analyzing each frame
            while current_game == games_completed:
                if current_state == State.INACTIVE:
                    time.sleep(3)
                    client.activateAutoKick()
                    current_state = State.IN_PLAY
                frame = cam.read()
                frame = perspective.applyPerspectiveTransform(frame)
                cropped_frame = frame[ai_config.y_minimum:ai_config.y_maximum, ai_config.x_right_minimum: ai_config.x_left_maximum].copy()
                gray = Circles.prep(cropped_frame)
                img = cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
                img = cv2.resize(img,(290,135))
                img = img.astype('float32')
                img = np.expand_dims(img,axis=0)
                prediction, label, confidence = predict.prediction(img,model)


                # Controls flippers
                match prediction:
                    case 0: 
                        UseFlipperLogic(flippers["left"],True)
                        #if not flippers["left"].active and datetime.now().timestamp() > flippers["left"].last_modified+ai_config.flipper_cooldown:
                            #flippers["left"].Activate(client)
                    case 1:
                        UseFlipperLogic(flippers["right"],True)
                        #if not flippers["right"].active and datetime.now().timestamp() > flippers["right"].last_modified+ai_config.flipper_cooldown:
                            #flippers["right"].Activate(client)
                    case _:
                        print('no action')

                # Deactivates flippers as necessary
                if flippers["left"].active and datetime.now().timestamp() >= flippers["left"].last_modified+ai_config.flipper_timeout:
                    flippers["left"].Deactivate(client)

                if flippers["right"].active and datetime.now().timestamp() >= flippers["right"].last_modified+ai_config.flipper_timeout:
                    flippers["right"].Deactivate(client)

                cv2.rectangle(frame,(400,28),(525,175),255,3)
                cv2.rectangle(frame,(235,28),(360,175),255,3)
                cv2.imshow('Machine Vision', gray)

                # Check if a ball was drained
                ball_drained, num_balls_drained = client.readBallDrain()
                if ball_drained and num_balls_drained > 0:

                    current_state = State.INACTIVE
                    print(f"Ball: {num_balls_drained} drained")

                    # No balls left in game
                    if num_balls_drained >= ai_config.balls_per_game:
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
        flippers["left"].Deactivate(client)
        flippers["right"].Deactivate(client)
        client.client.close()

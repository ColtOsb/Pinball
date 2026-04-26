#! /usr/bin/env python3
import cv2
import numpy as np
from control import PLCConnection
from perspective import Perspective
from vision import Circles
from datetime import datetime
from config import AI as ai_config
import VideoCapture
#Centimeter = 5.3 px
from enum import Enum
from flipper import Flipper
import time

from ultralytics import YOLO

class State(Enum):
    KILL = 0
    INACTIVE = 1
    OUT_OF_PLAY = 2
    IN_PLAY = 3


def UseFlipperLogic(client, flipper: Flipper, enable_output: bool = False):
    if not flipper.active and datetime.now().timestamp() > flipper.last_modified + ai_config.flipper_cooldown:
        flipper.Activate(client)
    if enable_output:
        print(flipper)


def Overlapping(box_a, box_b):
    box_a_x1, box_a_y1, box_a_x2, box_a_y2 = box_a.tolist()
    box_b_x1, box_b_y1, box_b_x2, box_b_y2 = box_b.tolist()

    if box_a_y1 < box_b_y2:
        if box_a_x2 > box_b_x1 and box_a_x2 <= box_b_x2:
            return True
        if box_a_x1 <= box_b_x2 and box_a_x1 > box_b_x1:
            return True
    return False



classes = {"ball": 0, "flipper-left": 1, "flipper-right": 2}

def Main():
    client = PLCConnection()
    current_state = State.OUT_OF_PLAY

    client.connectToPlc()

    games_to_play = ai_config.numRounds
    games_completed = 0
    flippers = {
        "left": Flipper(Flipper.sides.LEFT),
        "right": Flipper(Flipper.sides.RIGHT),
    }

    model = YOLO("models/best.engine")

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
                results = model.predict(source=frame, stream=True, conf=0.5, verbose=False)

                ball_location = None
                flipper_left_location = None
                flipper_right_location = None

                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls.cpu())
                        if cls == classes["ball"]:
                            ball_location = box.xyxy[0]
                            print(ball_location)
                        elif cls == classes["flipper-left"]:
                            flipper_left_location = box.xyxy[0]
                        elif cls == classes["flipper-right"]:
                            flipper_right_location = box.xyxy[0]

    
                # Activates flippers as necessary
                if ball_location is not None:
                    print(f"Ball: {ball_location}. Left: {flipper_left_location}. Right: {flipper_right_location}")
                    if flipper_left_location is not None:
                        if(Overlapping(ball_location, flipper_left_location)):
                            print("FLIP LEFT")
                            UseFlipperLogic(client,flippers["left"],True)
                    if flipper_right_location is not None:
                        if(Overlapping(ball_location, flipper_right_location)):
                            print("FLIP RIGHT")
                            UseFlipperLogic(client,flippers["right"],True)


                # Deactivates flippers as necessary
                if flippers["left"].active and datetime.now().timestamp() >= flippers["left"].last_modified+ai_config.flipper_timeout:
                    flippers["left"].Deactivate(client)

                if flippers["right"].active and datetime.now().timestamp() >= flippers["right"].last_modified+ai_config.flipper_timeout:
                    flippers["right"].Deactivate(client)
                """

                #cv2.rectangle(frame,(400,28),(525,175),255,3)
                #cv2.rectangle(frame,(235,28),(360,175),255,3)
                #cv2.imshow('Machine Vision', gray)
                
                """
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
        #client.client.close()

if __name__ == "__main__":
    Main()

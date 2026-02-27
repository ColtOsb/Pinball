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
#Centimeter = 5.3 px


if __name__ == "__main__":
    model = predict.loadModel()
    client = PLCConnection()
    if(client.connectToPlc()):
        print("PLC Connected")
        try:
            leftActive = False
            rightActive = False
            passiveState = False
            leftActivated = 0
            rightActivated = 0
            drainTime = 0
            kickCount = 0
            gameCount = 0
            roundEndTime = 0
            firstKickTimer = 0
            firstKickComplete = False
            execution_times = {"perspective":[],
                              "circle_prep":[],
                              "circle_detect":[],
                              "circle_locate":[],
                              "flipper":[],
                              "display":[]
                              }
            print(f"Tick frequency: {cv2.getTickFrequency()}")
            cam = cv2.VideoCapture(0)
            perspective = Perspective()
            client.startGame()
            gameCount += 1

            while True:
                ret, frame = cam.read()
                time_start = cv2.getTickCount()
                frame = perspective.applyPerspectiveTransform(frame)
                execution_times["perspective"].append((time_start,cv2.getTickCount()))
                #frame = zoom_at(frame,1.5)
                time_start = cv2.getTickCount()
                cropped_frame = frame[ai_config.y_minimum:ai_config.y_maximum, ai_config.x_right_minimum: ai_config.x_left_maximum].copy()
                gray = Circles.prep(cropped_frame)
                execution_times["circle_prep"].append((time_start,cv2.getTickCount()))
                time_start = cv2.getTickCount()
                circles = Circles.detectCircles(gray)
                execution_times["circle_detect"].append((time_start,cv2.getTickCount()))
                time_start = cv2.getTickCount()
                location = Circles.locateCircles(circles)
                execution_times["circle_locate"].append((time_start,cv2.getTickCount()))
                time_start = cv2.getTickCount()
                gray = cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
                gray = cv2.resize(gray,(290,135))
                prediction = predict.prediction(gray,model)
                if not firstKickComplete:
                    if not firstKickTimer:
                        firstKickTimer = datetime.now().timestamp()
                    elif datetime.now().timestamp() >= firstKickTimer + ai_config.kickerCooldown:
                        client.activateAutoKick()
                        firstKickComplete = True
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

                execution_times["flipper"].append((time_start,cv2.getTickCount()))
                time_start = cv2.getTickCount()
                Circles.displayCircles(circles,frame,offset=(ai_config.x_right_minimum,ai_config.y_minimum))
                cv2.rectangle(frame,(400,28),(525,175),255,3)
                cv2.rectangle(frame,(235,28),(360,175),255,3)
                cv2.imshow('Machine Vision', gray)
                execution_times["display"].append((time_start,cv2.getTickCount()))

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
            cam.release()
            cv2.destroyAllWindows()
            for key,x in execution_times.items():
                total = 0
                for y in x:
                    total += (y[1] - y[0]) / cv2.getTickFrequency()
                print(f"Total time spent on {key}: {total} over {len(x)} iterations. Average: {total/len(x)}")
                    
        finally:
            client.client.close()

#! /usr/bin/env python3
import cv2
import numpy as np
from control import PLCConnection
from perspective import Perspective
from vision import Circles
from datetime import datetime
from config import AI as ai_config

if __name__ == "__main__":

    client = PLCConnection()
    if(client.connectToPlc()):
        print("PLC Connected")
        try:
            leftActive = False
            rightActive = False
            leftActivated = 0
            rightActivated = 0

            execution_times = {"perspective":[],
                              "circle_prep":[],
                              "circle_detect":[],
                              "circle_locate":[],
                              "flipper":[],
                              "display":[]
                              }
            cam = cv2.VideoCapture(0)
            perspective = Perspective()
            while True:
                ret, frame = cam.read()
                time_start = cv2.getTickCount()
                frame = perspective.applyPerspectiveTransform(frame)
                execution_times["perspective"].append((time_start,cv2.getTickCount()))
                #frame = zoom_at(frame,1.5)
                time_start = cv2.getTickCount()
                gray = Circles.prep(frame)
                execution_times["circle_prep"].append((time_start,cv2.getTickCount()))
                time_start = cv2.getTickCount()
                circles = Circles.detectCircles(gray)
                execution_times["circle_detect"].append((time_start,cv2.getTickCount()))
                time_start = cv2.getTickCount()
                location = Circles.locateCircles(circles)
                execution_times["circle_locate"].append((time_start,cv2.getTickCount()))
                time_start = cv2.getTickCount()
                if location[0] >= 0 and location [1] >= 0:
                    print(location)
                x = location[0]
                y = location[1]
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
                Circles.displayCircles(circles,frame)
                cv2.rectangle(frame,(400,28),(525,175),255,3)
                cv2.rectangle(frame,(235,28),(360,175),255,3)
                cv2.imshow('Machine Vision', frame)
                execution_times["display"].append((time_start,cv2.getTickCount()))

                if cv2.waitKey(1) == ord('q'):
                    break
            cam.release()
            cv2.destroyAllWindows()
            for key,x in execution_times.items():
                total = 0
                for y in x:
                    total += (y[0] - y[1]) / cv2.getTickFrequency()
                print(f"Total time spent on {key}: {total} over {len(x)} iterations. Average: {total/len(x)}")
                    
        finally:
            client.client.close()

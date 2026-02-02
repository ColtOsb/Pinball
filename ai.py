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

            cam = cv2.VideoCapture(0)
            perspective = Perspective()
            while True:
                ret, frame = cam.read()
                frame = perspective.applyPerspectiveTransform(frame)
                #frame = zoom_at(frame,1.5)
                gray = Circles.prep(frame)
                circles = Circles.detectCircles(gray)
                location = Circles.locateCircles(circles)
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
                Circles.displayCircles(circles,frame)
                cv2.rectangle(frame,(400,28),(525,175),255,3)
                cv2.rectangle(frame,(235,28),(360,175),255,3)
                cv2.imshow('Machine Vision', frame)

                if cv2.waitKey(1) == ord('q'):
                    break
            cam.release()
            cv2.destroyAllWindows()
        finally:
            client.client.close()

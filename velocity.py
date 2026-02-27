import cv2
import numpy as np
from datetime import datetime
import time
from vision import Circles 
from perspective import Perspective
from config import AI as ai_config
import math
from datetime import datetime

#5.3 pixels per cm
def getVelocity(xStart, xEnd, yStart, yEnd,time):
    dX = abs(xStart - xEnd)
    dY = abs(yStart - yEnd)
    displacement = math.sqrt((dX ** 2) + (dY ** 2))
    velocity = displacement / time
    velocityCM = velocity/5.3
    #print("velocity in px/s {}".format(velocity))
    print("velocity in cm/s {}".format(velocityCM))
    return velocity


if __name__ == "__main__":
    cam = cv2.VideoCapture(0)
    perspective = Perspective()
    xStart = xEnd = yStart = yEnd = 0
    timeFrameOne = 0
    while True:
        ret, frame = cam.read()
        frame = perspective.applyPerspectiveTransform(frame)
        cropped_frame = frame[ai_config.y_minimum:ai_config.y_maximum, ai_config.x_right_minimum: ai_config.x_left_maximum].copy()
        gray = Circles.prep(cropped_frame)
        circles = Circles.detectCircles(gray)
        location = Circles.locateCircles(circles)

        if location[0] >= 0 and location[1] >= 0:
            if not xStart and not yStart:
                xStart = location[0]
                yStart = location[1]
                timeFrameOne = datetime.now().timestamp()
            else:
                xEnd = location[0]
                yEnd = location[1]
                time = datetime.now().timestamp() - timeFrameOne
                getVelocity(xStart,xEnd,yStart,yEnd,time)
                xStart = 0
                yStart = 0
        cv2.imshow("Velocity",gray)

        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

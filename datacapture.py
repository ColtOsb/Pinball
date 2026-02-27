import cv2
import os
import numpy as numpy
from vision import Circles
from perspective import Perspective
from config import AI as ai_config

if __name__ == "__main__":
    path = "/home/pi/vision/dataset"
    image_num = 0
    cam = cv2.VideoCapture(0)
    perspective = Perspective()

    while True:

        ret, frame = cam.read()
        frame = perspective.applyPerspectiveTransform(frame)
        cropped_frame = frame[ai_config.y_minimum:ai_config.y_maximum, ai_config.x_right_minimum: ai_config.x_left_maximum].copy()
        gray = Circles.prep(cropped_frame)
        cv2.imshow("Image",gray)
        cv2.imwrite(os.path.join(path , 'image{}.jpg'.format(image_num)), gray)
        image_num += 1

        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()


    
    

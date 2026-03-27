
import cv2
import numpy as np
from perspective import Perspective
from vision import Circles
from config import AI as ai_config
from copy import copy
import math
import predict
import VideoCapture
if __name__ == "__main__":
    model = predict.loadModel()
    cam = VideoCapture.VideoCapture(0)
    perspective = Perspective()

    while True:
        frame = cam.read()
        
        frame = perspective.applyPerspectiveTransform(frame)
        cropped_frame = frame[ai_config.y_minimum:ai_config.y_maximum, ai_config.x_right_minimum: ai_config.x_left_maximum].copy()
        gray = Circles.prep(cropped_frame)
        circles = Circles.detectCircles(gray)
        img = cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
        img = cv2.resize(img,(290,135))
        img = img.astype('float32') / 255.0
        img = np.expand_dims(img,axis=0)
        prediction = predict.prediction(img,model)
        cv2.imshow("frame", gray) 
        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()

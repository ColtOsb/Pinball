
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
        #original_img = cv2.imread('/home/pi/pinball/test_img/flip_right/imageI885.jpg')
        frame = cam.read()
        frame = perspective.applyPerspectiveTransform(frame)

        cropped_frame = frame[ai_config.y_minimum:ai_config.y_maximum, ai_config.x_right_minimum: ai_config.x_left_maximum].copy()

        gray = Circles.prep(cropped_frame)
#        cropped_img = original_img[ai_config.y_minimum:ai_config.y_maximum, ai_config.x_right_minimum: ai_config.x_left_maximum].copy()
#        img = Circles.prep(cropped_img)
        #img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
        img = cv2.resize(img,(290,135))
        img = img.astype('float32')
        img = np.expand_dims(img,axis=0) 
        predicted_index, label, confidence = predict.prediction(img,model)

        cv2.imshow("frame", frame) 
        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()

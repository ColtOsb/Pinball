
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

    while True:
        original_img = cv2.imread('/home/pi/pinball/dataset/no_action/imageF0.jpg')

        cropped_img = original_img[ai_config.y_minimum:ai_config.y_maximum, ai_config.x_right_minimum: ai_config.x_left_maximum].copy()
        img = Circles.prep(cropped_img)
        img = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
        img = cv2.resize(img,(290,135))
        img = img.astype('float32') / 255.0
        img = np.expand_dims(img,axis=0) 
        predicted_index = predict.prediction(img,model)
        label = predict.classes[predicted_index]
        print(f"Prediction: {label}")
        cv2.imshow("frame", original_img) 
        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()

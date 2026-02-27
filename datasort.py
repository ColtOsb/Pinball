import cv2
import os
import numpy as nup
from vision import Circles
import subprocess
import glob

quadrant_tl = (127, 22)
quadrant_tr = (48, 82)
quadrant_bl = (185, 23)
quadrant_br = (257, 80)


def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename),cv2.IMREAD_GRAYSCALE)
        if img is not None:
            images.append((filename, img))
    return images



if __name__ == "__main__":
    path = "/home/pi/vision/dataset/"
    y_minimum = 10
    y_maximum = 92
    x_right_minimum = 38
    x_right_maximum = 137
    x_left_minimum = 175
    x_left_maximum = 267
    for filename, img in load_images_from_folder(path):
        cv2.imshow("image",img)
        cv2.waitKey(5)
        if img is not None:
            circles = Circles.detectCircles(img)
            location = Circles.locateCircles(circles)
            x = location[0]
            y = location[1]
            if y >= y_minimum and y < y_maximum:
                if x >= x_right_minimum and x < x_right_maximum:
                    subprocess.call("mv {}/{} {}/flip_right".format(path,filename,path),shell=True)
                elif x >= x_left_minimum and x < x_left_maximum:
                    subprocess.call("mv {}/{} {}/flip_left".format(path,filename,path),shell=True)
                else:
                    subprocess.call("mv {}/{} {}/no_action".format(path,filename,path),shell=True)
            else:
                subprocess.call("mv {}/{} {}/no_action".format(path,filename,path),shell=True)
    print("Files Sorted")
        

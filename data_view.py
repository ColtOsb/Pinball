
import cv2
import os
import numpy as nup
from vision import Circles
import subprocess
import glob
from datasort import load_images_from_folder

if __name__ == "__main__":
    path_no_action = "/home/pi/vision/dataset/no_action/"
    path_flip_right = "/home/pi/vision/dataset/flip_right"
    path_flip_left = "/home/pi/vision/dataset/flip_left/"

    no_action_images = load_images_from_folder(path_no_action)
    flip_right_images = load_images_from_folder(path_flip_right)
    flip_left_images = load_images_from_folder(path_flip_left)

    for filename, img in no_action_images:
        cv2.imshow("NO ACTION",img)
        cv2.waitKey(10)
    for filename, img in flip_right_images:
        cv2.imshow("FLIP RIGHT",img)
        cv2.waitKey(10)
    for filename, img in flip_left_images:
        cv2.imshow("FLIP LEFT",img)
        cv2.waitKey(10)


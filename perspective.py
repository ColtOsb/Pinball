import numpy as np
import cv2

from config import PerspectiveCalibration as config

class Perspective:
    source_points = np.float32([config.quadrant_tl,config.quadrant_tr,config.quadrant_bl,config.quadrant_br])
    def __init__(self,source_points = None,debug=None):
        self.source_points = None
        if source_points == None:
            self.source_points = source_points = np.float32([config.quadrant_tl,config.quadrant_tr,config.quadrant_bl,config.quadrant_br])
        else:
            self.source_points = np.float32(source_points)
        self.width = max(config.quadrant_tr[0] - config.quadrant_tl[0],config.quadrant_br[0] - config.quadrant_bl[0])
        self.height = max(config.quadrant_br[1] - config.quadrant_tr[1],config.quadrant_bl[1] - config.quadrant_tl[1])

        self.width *= 2
        self.height *=2

        self.destination_points = np.float32([(0,0),(self.width,0),(0,self.height),(self.width,self.height)])
        self.output_size = (self.width,self.height)
        self.matrix = cv2.getPerspectiveTransform(self.source_points,self.destination_points)
        self.debug = False
        if debug is None:
            self.debug = config.debug
        if self.debug:
            print(f"Width: {self.width}, Height: {self.height}")
            print(f"Source Points: \n{self.source_points}")
            print(f"Destination Points: \n{self.destination_points}")
            print(f"Output Size: {self.output_size}")
    def applyPerspectiveTransform(self,frame):
        return cv2.warpPerspective(frame,self.matrix,self.output_size)

def PerspectiveTransform(imageFrame,source_points):
    #source_points = np.float32(source_points)
    #destination_points = np.float32([[0,0],[3840,0],[0,2160],[3840,2160]])
    transformed_image = cv2.warpPerspective(imageFrame,matrix,output_size)
    return transformed_image

def calibratePerspectiveTransform(webcam,debug=False):

    perspective = Perspective()
    while True:
        #print('new frame')
        ret, frame = webcam.read()

        warped_frame = perspective.applyPerspectiveTransform(frame)

        cv2.imshow("Color detection",warped_frame)
                
        if cv2.waitKey(1) == ord('q'):
            break
    webcam.release()
    cv2.destroyAllWindows()
                    
if __name__ == "__main__":
    cam = cv2.VideoCapture(0)
    calibratePerspectiveTransform(cam,config.debug)

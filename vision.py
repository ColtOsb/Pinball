import cv2
import numpy as np
from perspective import Perspective
from config import CircleDetection as config
from datetime import datetime

def zoom_at(img, zoom, coord=None):
    """
    Simple image zooming without boundary checking.
    Centered at "coord", if given, else the image center.

    img: numpy.ndarray of shape (h,w,:)
    zoom: float
    coord: (float, float)
    """
    # Translate to zoomed coordinates
    h, w, _ = [ zoom * i for i in img.shape ]
    
    if coord is None: cx, cy = w/2, h/2
    else: cx, cy = [ zoom*c for c in coord ]
    
    img = cv2.resize( img, (0, 0), fx=zoom, fy=zoom)
    img = img[ int(round(cy - h/zoom * .5)) : int(round(cy + h/zoom * .5)),
               int(round(cx - w/zoom * .5)) : int(round(cx + w/zoom * .5))
              ]
    
    return img

def getFPS(cam): 
    numFrames = 120
    start = time.time()

    for i in range (0,numFrames):
        ret, frame = cam.read()
    end = time.time()
    seconds = end-start
    print("Seconds: {}".format(seconds))
    fps = numFrames / seconds

    print("FPS: {}".format(fps))

    return fps


class Circles:

    def prep(frame):
        max_value = 255
        max_binary_value = 255
        trackbar_type = 1 
        trackbar_value = 'Value'
        
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        threshold_type = 1
        threshold_value = 170
        _, dst = cv2.threshold(gray, threshold_value, max_binary_value, threshold_type )

        kernel = np.ones((3,3),np.uint8)
        img_dilated = cv2.dilate(dst,kernel,iterations=1)

        return img_dilated

    def detectCircles(dst):
        circles = cv2.HoughCircles(
                dst,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=20,
                param1=config.param1,
                param2=config.param2,
                minRadius=config.minRadius,
                maxRadius=config.maxRadius
                )
        return circles

    def displayCircles(circles,frame,offset=(0,0)):
        if circles is not None:
            circles = np.uint16(np.around(circles))
            x, y, r = circles[0][0]
            x += offset[0]
            y += offset[1]
            cv2.circle(frame, (x,y),r,(0,255,0), 2)
            cv2.circle(frame, (x,y), 2, (0,0,255),3)
            print(r)
        return frame

    def locateCircles(circles):
        if circles is not None:
            circles = np.uint16(np.around(circles))
            x, y, r = circles[0][0]
            return (x,y)
        else:
            return (-1,-1)


if __name__ == "__main__":
    cam = cv2.VideoCapture(0)
    perspective = Perspective()
    while True:
        ret, frame = cam.read()
        frame = perspective.applyPerspectiveTransform(frame)
        dst = Circles.prep(frame)
        frame = Circles.displayCircles(Circles.detectCircles(dst),dst)
        

        cv2.imshow('Detected Circle', dst)

        if cv2.waitKey(1) == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()

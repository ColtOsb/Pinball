import cv2
import numpy as np

cam = cv2.VideoCapture(0)
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))


while True:
    ret, frame = cam.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray,5)

    circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=100,
            param1=100,
            param2=40,
            minRadius=30,
            maxRadius=60
            )
    if circles is not None:
        circles = np.uint16(np.around(circles))
        x, y, r = circles[0][0]
        cv2.circle(frame, (x,y),r,(0,255,0), 2)
        cv2.circle(frame, (x,y), 2, (0,0,255),3)

    

    cv2.imshow('Detected Circle', frame)

    if cv2.waitKey(1) == ord('q'):
        break
cam.release()
out.release()
cv2.destroyAllWindows()

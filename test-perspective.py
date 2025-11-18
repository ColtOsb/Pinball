import numpy as np
import cv2

import config

#imageFrame = cv2.imread("/home/user/shared/test_colors.jpg")

def calibratePerspectiveTransform(webcam,debug=False):

    while (1):
        _, imageFrame = webcam.read()
        #imageFrame = cv2.imread("/home/user/shared/test_colors.jpg")

        # Convert BGR to HSV colorspace
        hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

        #blue color
        #blue_lower = np.array([94, 80, 2], np.uint8)
        #blue_upper = np.array([120, 255, 255], np.uint8)
        blue_mask = cv2.inRange(hsvFrame, config.PerspectiveCalibration.blue_lower,config.PerspectiveCalibration.blue_upper)


        # to detect only that particular color
        kernal = np.ones((5, 5), "uint8")

        # blue color
        blue_mask = cv2.dilate(blue_mask, kernal)
        res_blue = cv2.bitwise_and(imageFrame, imageFrame, mask=blue_mask)


        # Creating contour to track blue color
        contours, hierarchy = cv2.findContours(blue_mask,
                                               cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
        source_points = []
        for _, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if (area > 300):
                x, y, w, h = cv2.boundingRect(contour)
                if y > config.PerspectiveCalibration.horizontal_median:
                    if x > config.PerspectiveCalibration.vertical_median:
                        source_points.append([x,y])
                        color = config.PerspectiveCalibration.color_quadrant_tl
                        if debug:
                            print("Top left: ",end="")
                    else:
                        source_points.append([x+w,y])
                        color = config.PerspectiveCalibration.color_quadrant_tr
                        if debug:
                            print("Top right: ",end="")
                else:
                    if x > config.PerspectiveCalibration.vertical_median:
                        source_points.append([x,y+h])
                        color = config.PerspectiveCalibration.color_quadrant_bl
                        if debug:
                            print("Bottom left: ",end="")
                    else:
                        source_points.append([x+w,y+h])
                        color = config.PerspectiveCalibration.color_quadrant_br
                        if debug:
                            print("Bottom right: ",end="")
                if debug:
                    print(f"({source_points[-1][0]},{source_points[-1][1]})")
                #continue
                imageFrame = cv2.rectangle(imageFrame, (x, y),
                                           (x + w, y + h),
                                           (255, 0, 0), 2)
                imageFrame = cv2.circle(imageFrame,(source_points[-1]),2,color,2)

        
        """
        source_points = np.float32(source_points)
        print(source_points)
        destination_points = np.float32([[0,0],[640,0],[0,480],[640,480]])
        print(destination_points)
        matrix = cv2.getPerspectiveTransform(source_points,destination_points)
        transformed_image = cv2.warpPerspective(imageFrame,matrix,(640,480))
        imageFrame = transformed_image
        """
        # final run
        cv2.imshow("Color Detection", imageFrame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            webcam.release()
            cv2.destroyAllWindows()
            break

if __name__ == "__main__":

    calibratePerspectiveTransform(cv2.VideoCapture(2),config.PerspectiveCalibration.debug)

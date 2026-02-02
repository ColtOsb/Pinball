import numpy as np

class PerspectiveCalibration:
    #blue_lower = np.array([94,80,2],np.uint8)
    #blue_upper = np.array([120,255,255],np.uint8)

    #blue_lower = np.array([32,32,32],np.uint8)
    #blue_upper = np.array([96,96,96],np.uint8)

    quadrant_tl = (165,74)
    quadrant_tr = (506,76)
    quadrant_bl = (154,225)
    quadrant_br = (518,224)

    color_quadrant_tl = (0,255,0) # Green
    color_quadrant_tr = (0,0,255) # Red
    color_quadrant_bl = (255,0,255) # Purple
    color_quadrant_br = (0,255,255) # Yellow

    #vertical_median = 400
    #horizontal_median = 200
    debug = True

class CircleDetection:
    minRadius = 12
    maxRadius = 15
    param1 = 130
    param2 = 15

class AI:
    flipper_timeout = 0.5
    flipper_cooldown = 0.2
    y_minimum = 40
    y_maximum = 175
    x_left_minimum = 400
    x_left_maximum = 525
    x_right_minimum = 235
    x_right_maximum = 360

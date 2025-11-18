import numpy as np
class PerspectiveCalibration:
    blue_lower = np.array([94,80,2],np.uint8)
    blue_upper = np.array([120,255,255],np.uint8)
    
    # The colors to display the location of the perspective transform
    # Note that colors are in BGR format, not RGB because of cv2
    color_quadrant_tl = (0,255,0) # Green
    color_quadrant_tr = (0,0,255) # Red
    color_quadrant_bl = (0,0,0) # Black
    color_quadrant_br = (0,255,255) # Yellow
    
    # Pixels that identify which quadrant the piece of tape is in
    vertical_median = 400
    horizontal_median = 350

    debug = True

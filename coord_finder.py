import cv2
from time import time
from config import PerspectiveCalibration as pc
from perspective import Perspective

class CoordConfig:
    def __init__(self):
        self.coords_name = ["tl","tr","bl","br"]
        self.coords = {"tl": {
                    "color": pc.color_quadrant_tl,
                    "location": (-1,-1)
                 },
                "tr": {
                    "color": pc.color_quadrant_tr,
                    "location": (-1,-1)
                 },
                "bl": {
                    "color": pc.color_quadrant_bl,
                    "location": (-1,-1)
                 },
                "br": {
                    "color": pc.color_quadrant_br,
                    "location": (-1,-1)
                 }
            }
        self.coords_index = 0

    def on_mouse(self,event,x,y,flags,params):
        t = time()

        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"({x},{y})")
            self.coords[self.coords_name[self.coords_index]]["location"] = (x,y)
            self.coords_index = (self.coords_index + 1) % 4
            print(f"Coordinate {self.coords_name[self.coords_index]}: ",end="",flush=True)

    def displayCoords(self):
        for value in self.coords.values():
            if not (value["location"][0] == -1 or value["location"][1] == -1):
                cv2.circle(self.frame,value["location"],3,value["color"],-1)
    
    def run(self):

        cam = cv2.VideoCapture(0)
        perspective = Perspective()
        print("Click on the screen to print the coordinate location. Press q to exit. You can loop as many times as you would like.")
        print(f"Coordinate {self.coords_name[self.coords_index]}: ",end="",flush=True)
        while(1):

            ret, self.frame = cam.read()
            self.frame = perspective.applyPerspectiveTransform(self.frame)
            #img = cv2.resize(img,None,fx=0.25,fy=0.25)
            self.displayCoords()

            cv2.namedWindow('real image')
            cv2.setMouseCallback('real image', self.on_mouse, 0)
            cv2.imshow('real image', self.frame)

            if cv2.waitKey(1) == ord("q"):
                break
        cam.release()
        cv2.destroyAllWindows()
        print()
        for key,value in self.coords.items():
            print(f"quadrant_{key} = {value['location']}")

if __name__ == "__main__":
    x = CoordConfig()
    x.run()

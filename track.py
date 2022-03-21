import cv2
import numpy as np
import os
import imutils
from imutils import contours
from WandObserver import WandObserver
import math

def get_points(frame):
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray , (9, 9), 0)
    thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=4)

    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    good_pt = []
    if len(cnts)>0:
        cnts = contours.sort_contours(cnts)[0]
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
        # loop over the contours
        for (i, c) in enumerate(cnts):
            # draw the bright spot on the image
            (x, y, w, h) = cv2.boundingRect(c)
            ((cX, cY), radius) = cv2.minEnclosingCircle(c)
            if radius < 1 or radius > 18:
                continue
            # good_pt.append(((cX, cY), radius))
            good_pt.append((cX, cY))
            cv2.circle(frame, (int(cX), int(cY)), int(radius),(255,102,51), 3)
            # cv2.putText(frame, "#{}".format(i + 1), (x, y - 15),
            # cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
    return good_pt

def main():
    wand1 = WandObserver("wand1",[1,0,1,0,1,0,1,0],(102,204,255))
    wand2 = WandObserver("wand2",[1,1,0,0,1,1,0,0],(0,255,0))
    wands = [wand1,wand2]
    videofile_path = "./data/test.mp4"
    cap = cv2.VideoCapture(videofile_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_all = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    print("[INFO] FPS: {}".format(fps))
    print("[INFO] total frame: {}".format(frame_all))
    print("[INFO] time: {}s".format(frame_all/fps))

    rval, frame = cap.read()
    count = 0
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    videowriter = cv2.VideoWriter("./output/output.mp4",fourcc, 30, (width,height))
    while 1:
        # print(count)
        rval, frame = cap.read()
        if not rval:
            break
        count += 1
        points = get_points(frame)

        for wand in wands:
            wand(points)
            wand.draw(frame)
        videowriter.write(frame)
        
    videowriter.release()
    cv2.waitKey(0)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
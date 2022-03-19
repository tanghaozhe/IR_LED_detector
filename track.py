import cv2
from cv2 import threshold
import numpy as np
import os
import imutils
from imutils import contours
from modules import WandObserver
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
            if radius < 8 or radius > 18:
                continue
            # good_pt.append(((cX, cY), radius))
            good_pt.append((cX, cY))
            cv2.circle(frame, (int(cX), int(cY)), int(radius),(255, 0, 0), 3)
            # cv2.putText(frame, "#{}".format(i + 1), (x, y - 15),
            # cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
    return good_pt

def get_signal_num(diff_frames):
    if diff_frames >= 13:
        wand_signal_n = 2
    elif diff_frames >= 0 and diff_frames <= 13:
        wand_signal_n = 1
    return wand_signal_n

def main():
    wand1 = WandObserver("wand1",[1,0,1,0],(0,0,255))
    wand2 = WandObserver("wand2",[1,1,0,0],(0,255,0))
    wands = [wand1,wand2]
    videofile_path = "./data/0.5.mp4"
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
        rval, frame = cap.read()
        if not rval:
            break
        # filename = os.path.sep.join(["./output", "test_{}".format(count)])
        count += 1
        points = get_points(frame)

        for wand in wands:
            wand.diff_frames += 1
            is_signal_changed = False
            cur_signal = 0
            stroke_ix = wand.stroke_ix
            if len(points) > 0:
                if len(wand.points[stroke_ix]) > 0:
                    pre_point = wand.points[stroke_ix][-1]
                    dists = [math.sqrt((pre_point[0]-s0)**2 + (pre_point[1]-s1)**2) for s0, s1 in points]
                    min_dist = min(dists)
                    if min_dist < 100:
                        cur_signal = 1
                        nt_point = points[dists.index(min_dist)]
                    else:
                        wand.abort()
                else:
                    cur_signal = 1
                    nt_point = points[0]  # FIXME     

            pre_signal = wand.pre_signal

            if pre_signal==0 and cur_signal==1:
                is_signal_changed = True
                wand_signal = 1
                wand_signal_n = get_signal_num(wand.diff_frames)
                # print("light frames:",wand.diff_frames,"count:",count)
                wand.diff_frames = 0

            elif pre_signal==1 and cur_signal==0:
                is_signal_changed = True
                wand_signal = 0
                # print("black frames:",wand.diff_frames,"count:",count)
                wand_signal_n = get_signal_num(wand.diff_frames)
                wand.diff_frames = 0

            if is_signal_changed:
                for i in range(wand_signal_n):
                    wand(wand_signal)

            if wand.is_detected:
                wand.points[stroke_ix].append(nt_point)
            
            wand.draw(frame)
        videowriter.write(frame)
        
    videowriter.release()
    cv2.waitKey(0)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
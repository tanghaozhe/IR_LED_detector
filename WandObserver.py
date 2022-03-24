from abc import ABCMeta
from abc import ABCMeta, abstractmethod
import cv2
import numpy as np
import math
from itertools import cycle
from scipy.special import comb

from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder

IP = '127.0.0.1'
PORT = 6700

# Create UDP client
client = udp_client.UDPClient(IP, PORT)

class Observer(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self) -> None:
        pass
    def update(self):
        pass
    def check(self):
        pass
    def abort(self):
        pass

class WandObserver(Observer):
    def __init__(self, name, template, color):
        self.name = name
        self.template = template
        self.is_detected = False
        self.points = [[]]
        self.bezier_curve_points = [[]]
        self.color = color
        self.frames_cnt = 0
        self.stroke_ix = 0
        self.pre_signal = template[0]
        self.cached_points = []
        self.input_signal = []
        self.template_iter = cycle(template)
        self.max_dist_bt_pts = 500
        self.bezier_curve = True

    def __call__(self,cur_points):
        if self.is_detected:
            self.frames_cnt += 1
            pre_signal = self.pre_signal
            cur_signal = 0
            nt_point = None
            if len(cur_points) != 0:
                if len(self.points[self.stroke_ix]) > 0:
                    pre_point = self.points[self.stroke_ix][-1]
                    dists = [math.sqrt((pre_point[0]-s0)**2 + (pre_point[1]-s1)**2) for s0, s1 in cur_points]
                    if min(dists) < self.max_dist_bt_pts:
                        cur_signal = 1
                        nt_point = cur_points[dists.index(min(dists))]
                else:
                    cur_signal = 1
                    nt_point = cur_points[0] # FIXME
                    
            is_signal_changed = True
            if not pre_signal and cur_signal:
                wand_signal_n = self.get_signal_num(self.frames_cnt)
                # print(self.name, " high signal frames:",self.frames_cnt)
                self.frames_cnt = 0
                self.pre_signal = 1
            elif pre_signal and not cur_signal:
                # print(self.name, " low signal frames:",self.frames_cnt)
                wand_signal_n = self.get_signal_num(self.frames_cnt)
                self.frames_cnt = 0
                self.pre_signal = 0
            else:
                is_signal_changed  = False
            if is_signal_changed:
                for _ in range(wand_signal_n):
                    self.update(pre_signal,nt_point)
                    if nt_point and self.bezier_curve:  # FIXME
                        self.points[self.stroke_ix].append(nt_point)
            elif len(cur_points) > 0:
                if not self.bezier_curve and nt_point:
                    self.points[self.stroke_ix].append(nt_point)
        else:
            self.check(cur_points)

    def update(self,signal,point):
        if next(self.template_iter) != signal:
            self.abort()
        if point:
            # Sent message to /data
            msg = OscMessageBuilder(address='/data')
            x, y, name =  point[0], point[1], self.name
            msg.add_arg(x)
            msg.add_arg(y)
            msg.add_arg(name)
            m = msg.build()
            client.send(m)

    def abort(self):
        self.stroke_ix += 1
        self.is_detected = False
        self.points.append([])
        self.bezier_curve_points.append([])
        self.diff_frames = 0
        self.pre_signal = self.template[0]
        self.cached_points.clear()
        print(f"{self.name} aborted!")

    def bernstein(self,n, i, t):
        return comb(n, i) * t**i * (1 - t)**(n-i)

    def bezier(self,n, t, pts):
        p = np.zeros(2)
        for i in range(n + 1):
            p += self.bernstein(n, i, t) * np.array(pts[i], dtype=np.int32)
        return tuple(p)

    def draw(self, frame):
        for ix, pts in enumerate(self.points):
            try:
                if self.bezier_curve:
                    if len(pts)>=4:
                        tmp = pts[:]
                        self.points[ix] = []
                        tmp_list = []
                        for t in np.linspace(0, 1, 50):
                            tmp_list.append(self.bezier(len(tmp)-1, t, pts))  
                        self.bezier_curve_points[ix].extend(tmp_list)
                    pts = np.array(self.bezier_curve_points[ix], dtype=np.int32)
                    cv2.polylines(frame,[pts],False,self.color,3)
                else:
                    pts = np.array(pts, dtype=np.int32)
                    cv2.polylines(frame,[pts],False,self.color,3)
                    # if len(pts) > 0:
                    #     for point in pts:
                    #         cv2.circle(frame, (int(point[0]),int(point[1])), 3,(255,102,51), 3)
            except Exception as e:
                print("drawing failed!")
    
    def get_signal_num(self,frames_cnt):
        if frames_cnt >= 13:
            wand_signal_n = 2
        elif frames_cnt >= 0 and frames_cnt <= 13:
            wand_signal_n = 1
        else:
            print("input signal invalid!")
        return wand_signal_n

    def check(self, cur_points):
        # matching signals with template pattern
        self.frames_cnt += 1
        if len(cur_points) > 0:
            cur_point = cur_points[0] # FIXME
            cur_signal = 1
        else:
            cur_signal = 0
        is_signal_changed = True
        pre_signal = self.pre_signal
        if not pre_signal and cur_signal:
            wand_signal_n = self.get_signal_num(self.frames_cnt)
            # print(self.name, " low signal frames:",self.frames_cnt)
            self.pre_signal = 1
            self.frames_cnt = 0
        elif pre_signal and not cur_signal:
            wand_signal_n = self.get_signal_num(self.frames_cnt)
            # print(self.name, " high signal frames:",self.frames_cnt)
            self.pre_signal = 0
            self.frames_cnt = 0
        else:
            is_signal_changed  = False
        if is_signal_changed:
            for _ in range(wand_signal_n):
                self.input_signal.append(pre_signal)
        
        input_signal_slice = self.input_signal[-len(self.template):]
        if input_signal_slice == self.template:
            self.is_detected = True
            self.input_signal.clear()
            self.points[self.stroke_ix].append(cur_point)
            print(self.name," detected!")

    
    
    

    
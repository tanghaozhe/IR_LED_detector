from abc import ABCMeta
from abc import ABCMeta, abstractmethod
from dis import dis
from re import template
import cv2
import numpy as np
import math

class Observer(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self) -> None:
        pass
    def update(self):
        pass

class WandObserver(Observer):
    def __init__(self, name, template, color):
        self.name = name
        self.template = template
        self.pointer = -1
        self.is_detected = False
        self.points = [[]]
        self.signals = []
        self.color = color
        self.frames_cnt = 0
        self.stroke_ix = 0
        self.pre_signal = template[0]
        self.cached_points = []


    def __call__(self,cur_points):
        if self.is_detected:
            self.frames_cnt += 1
            pre_signal = self.pre_signal
            if len(cur_points) == 0:
                cur_signal = 0
            pre_point = self.points[self.stroke_ix][-1]
            dists = [math.sqrt((pre_point[0]-s0)**2 + (pre_point[1]-s1)**2) for s0, s1 in cur_points]
            if len(dists) > 0 and min(dists) < 2000:
                cur_signal = 1
                nt_point = cur_points[dists.index(min(dists))]
            else:
                cur_signal = 0
                nt_point = None

            is_signal_changed = True
            if pre_signal==0 and cur_signal==1:
                wand_signal_n = self.get_signal_num(self.frames_cnt)
                # print(self.name, " light frames:",self.frames_cnt)
                self.frames_cnt = 0
                self.pre_signal = 1
            elif pre_signal==1 and cur_signal==0:
                # print(self.name, " black frames:",self.frames_cnt)
                wand_signal_n = self.get_signal_num(self.frames_cnt)
                self.frames_cnt = 0
                self.pre_signal = 0
            else:
                is_signal_changed  = False
            if is_signal_changed:
                for _ in range(wand_signal_n):
                    self.update(pre_signal, nt_point)
            elif len(cur_points) > 0:
                self.points[self.stroke_ix].append(nt_point)
        else:
            self.check_cached_points(cur_points)


    def check_cached_points(self, cur_points):
        # matching signals with template pattern
        cached_points = self.cached_points
        
        if len(cached_points) == 0:
            self.cached_points = [[(x,y),-1,1,1] for x,y in cur_points]  # fix pre_signal
            
        else:
            for ix,[point,pointer,pre_signal,frames_cnt] in enumerate(cached_points):
                cached_points[ix][3] += 1
                dists = [math.sqrt((point[0]-s0)**2 + (point[1]-s1)**2) for s0, s1 in cur_points]
                if len(dists) > 0 and min(dists) < 200:
                    cur_signal = 1
                else:
                    cur_signal = 0
                is_signal_changed = True

                if pre_signal==0 and cur_signal==1:
                    wand_signal_n = self.get_signal_num(frames_cnt)
                    print(self.name, " black frames:",frames_cnt)
                    cached_points[ix][2] = 1
                    cached_points[ix][3] = 0
                elif pre_signal==1 and cur_signal==0:
                    print(self.name, " light frames:",frames_cnt)
                    wand_signal_n = self.get_signal_num(frames_cnt)
                    cached_points[ix][2] = 0
                    cached_points[ix][3] = 0
                else:
                    is_signal_changed  = False
                if is_signal_changed:
                    for _ in range(wand_signal_n):
                        cached_points[ix][1] += 1
                        if self.template[cached_points[ix][1]] == pre_signal:
                            if cached_points[ix][1] >= len(self.template)-1:
                                self.is_detected = True
                                print(f"{self.name} detectd!")
                                self.points[self.stroke_ix].append(point)
                                break
                        else:
                            self.cached_points.clear()
                            print("Matching failed!")
                            break
                        

    def update(self,signal, nt_point):
        if self.pointer == len(self.template)-1:
            self.pointer = -1
        if self.template[self.pointer+1] != signal:
            self.abort()
        else:
            self.pointer += 1
            if nt_point:
                self.points[self.stroke_ix].append(nt_point)
            # print("updated!")
        

    def abort(self):
        self.stroke_ix += 1
        self.pointer = -1
        self.is_detected = False
        self.points.append([])
        self.signals = []
        self.diff_frames = 0
        self.pre_signal = self.template[0]
        self.cached_points.clear()
        print(f"{self.name} aborted!")

    def draw(self, frame):
        for pts in self.points:
            try:
                pts = np.array(pts, dtype=np.int32)
                cv2.polylines(frame,[pts],False,self.color,3)
            except Exception as e:
                print(e)
            
    
    def get_signal_num(self,frames_cnt):
        if frames_cnt >= 13:
            wand_signal_n = 2
        elif frames_cnt >= 0 and frames_cnt <= 13:
            wand_signal_n = 1
        else:
            print("signal invalid")
        return wand_signal_n

    
    
    

    
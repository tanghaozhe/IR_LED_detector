from abc import ABCMeta
from abc import ABCMeta, abstractmethod
import cv2
import numpy as np

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
        self.diff_frames = 0
        self.stroke_ix = 0
        self.pre_signal = 0

    def __call__(self,signal):
        self.signals.append(signal)
        self.pre_signal = signal
        if not self.is_detected:
            self.check(signal)
        else:
            self.update(signal)

    def check(self, signal):
        # matching signals with template pattern
        if self.template[self.pointer+1] == signal:
            self.pointer += 1
        else:
            self.pointer = -1
        if self.pointer == len(self.template)-1:
            self.is_detected = True
            self.pointer = 0
            print(f"{self.name} detectd!")

    def update(self,signal):
        if self.template[self.pointer] != signal:
            self.abort()
        else:
            self.pointer += 1
            # print("updated!")
        if self.pointer == len(self.template):
            self.pointer = 0

    def abort(self):
        self.stroke_ix += 1
        self.pointer = -1
        self.is_detected = False
        self.points.append([])
        self.signals = []
        self.diff_frames = 0
        self.pre_signal = 0
        print(f"{self.name} aborted!")

    def draw(self, frame):
        for pts in self.points:
            pts = np.array(pts, dtype=np.int32)
            cv2.polylines(frame,[pts],False,self.color,3)
        

    
    
    

    
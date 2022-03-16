class Wand:
    def __init__(self, name, template, color):
        self.name = name
        self.template = template
        self.pointer = -1
        self.detect_flag = False
        self.points = []
        self.signals = []
        self.color = color
        self.diff_frames = 0


    def check(self, signal):
        if self.template[self.pointer+1] == signal:
            self.pointer += 1
        else:
            self.pointer = -1
        if self.pointer == len(self.template)-1:
            self.detect_flag = True
            self.pointer = 0
            print("wand detectd!")

    def update(self,signal):
        if self.template[self.pointer] != signal:
            self.abort()
        else:
            self.pointer += 1
            # print("updated!")
        if self.pointer == len(self.template):
            self.pointer = 0

    def abort(self):
        self.pointer = -1
        self.detect_flag = False
        self.points = []
        self.signals = []
        self.diff_frames = 0
        print("aborted!")


# wand1 = Wand([0,1,1])
# records = []
# signals = []
# while 1:
#     points = input("input:")
#     if points:
#         points = [int(x) for x in points.split(" ")]
#         records.append([points])
#         signal = 1
#     else:
#         # print("nothing detected!")
#         records.append([])
#         signal = 0
#     signals.append(signal)
    
#     if not wand1.detect_flag:
#         wand1.check(signal)
#     else:
#         wand1.update(signal)
    # print("pointer:",wand1.pointer)
    
    

    
    
    

    
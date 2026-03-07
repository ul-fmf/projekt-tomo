
from collections import deque
import math


class NWMAFilter: #Non-weighted moving average

    def __init__(self, n):
        super(NWMAFilter, self).__init__()
        self.N = 2 * n + 1
        self.C = 1. / self.N
        self.data_x = deque(maxlen=self.N)
        self.data_y = deque(maxlen=self.N)
        self.data_t = deque(maxlen=self.N)
      

    def __call__(self, t, x, y):
        self.data_x.append(x)
        self.data_y.append(y)
        self.data_t.append(t)

        #print(self.data_x)
        #print(self.data_y)

        if len(self.data_x) == self.data_x.maxlen:
            #the buffer is full, the window is now full, compute the average
            x = self.C * sum(self.data_x)
            y = self.C * sum(self.data_y)
            t = self.data_t[self.N//2]
         
            return dict(x=x, y=y, timestamp=t)

class IVTFilter:

    def __init__(self, threshold):
        self.data_x = deque(maxlen=2)
        self.data_y = deque(maxlen=2)
        self.data_t = deque(maxlen=2)
        self.threshold = threshold

    def __call__(self, t, x, y): #estimate velocity using the two most recent samples... 
        self.data_x.append(x)
        self.data_y.append(y)
        self.data_t.append(t)

        l = len(self.data_x)

        dt = self.data_t[0 % l] - self.data_t[1 % l]
        if dt != 0:
           
            dx = self.data_x[0 % l] - self.data_x[1 % l]
            dy = self.data_y[0 % l] - self.data_y[1 % l]
            
            v = math.sqrt(dx **2 + dy ** 2) / abs(dt)

            if v > self.threshold:
                return dict(label='saccade', x=x, y=y, timestamp=t)
            else:
                return dict(label='gaze', x=x, y=y, timestamp=t)

class TobiiFilter:

    def __init__(self, n, threshold):
        super(TobiiFilter, self).__init__()
        self.ma = NWMAFilter(n)
        self.ivt = IVTFilter(threshold)

    def __call__(self, t, x, y):
        r = self.ma(t, x, y)
        if r is not None:
            return self.ivt(r['timestamp'], r['x'], r['y'])
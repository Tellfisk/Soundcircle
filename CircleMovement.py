import numpy as np
import random
from scipy.fftpack import fft

class SuperMovement(object):

    def __init__(self, radius, color, pos):
        self.first_draw = True
        self.pos = pos
        self.radius = radius
        self.color = color
        self.number_of_points = 1023
        self.increments = 2 / self.number_of_points

        self.prev_x = []
        self.prev_y = []
        t = 0
        while(t < 2):
            self.prev_x.append(self.pos + self.radius * np.cos(np.pi * t))
            self.prev_y.append(self.pos + self.radius * np.sin(np.pi * t))
            t += self.increments
        self.prev_x[-1] = self.prev_x[0]
        self.prev_y[-1] = self.prev_y[0]


    def smoothing(self, x, y):
        assert len(x) == len(self.prev_x), "x lists of different size!"
        assert len(y) == len(self.prev_y), "y lists of different size!"
        assert len(x) == len(y), "New x and y lists of different size!"
        smooth_tuple = ([], [])

        smooth_factor =  2  # Positive integer, including 0. 0 = no smoothing
        
        if smooth_factor > 0:
            for i in range(len(x)):
                smooth_tuple[0].append((x[i] + self.prev_x[i] * smooth_factor) / (smooth_factor + 1))
                smooth_tuple[1].append((y[i] + self.prev_y[i] * smooth_factor) / (smooth_factor + 1))
            self.prev_x = smooth_tuple[0]
            self.prev_y = smooth_tuple[1]
        else:
            return (x, y)
        return (smooth_tuple[0], smooth_tuple[1])


class RandomMovement(SuperMovement):
    def __init__(self, radius, color, pos):
        super().__init__(radius, color, pos)

    def update(self):
        x = []
        y = []
        t = 0
        rnd = random.randint(0, 100)
        while(t <= 2):
            is_rnd = random.randint(0, 400)
            if is_rnd == 1:
                rnd = random.randint(0, 100)
            x.append(self.pos + (self.radius + rnd) * np.cos(np.pi * t))
            y.append(self.pos + (self.radius + rnd) * np.sin(np.pi * t))
            t += self.increments
        x[-1] = x[0]
        y[-1] = y[0]
        #x.append(x[0])
        #y.append(y[0])
        cart_pair = (x, y)
        cart_pair = self.smoothing(x, y)
        return cart_pair


class WaveMovement(SuperMovement):
    def __init__(self, radius, color, pos):
        super().__init__(radius, color, pos)

    def update(self, in_data, CHUNK):
        data = np.frombuffer(in_data, dtype='h')
        data = np.array(data, dtype='h') / 300
        x = []
        y = []
        t = 0
        n = 0
        while(t <= 2):
            x.append(self.pos + (self.radius + data[n]) * np.cos(np.pi * t))
            y.append(self.pos + (self.radius + data[n]) * np.sin(np.pi * t))
            t += self.increments
            n += 1
        x[-1] = x[0]
        y[-1] = y[0]
        cart_pair = (x, y)
        cart_pair = self.smoothing(x, y)
        return cart_pair


class SpectrumMovement(SuperMovement):
    def __init__(self, radius, color, pos):
        super().__init__(radius, color, pos)

    
    def update(self, in_data, CHUNK):
        data = np.frombuffer(in_data, dtype='h')
        data = np.array(data, dtype='h')/10
        data = fft(np.array(data, dtype='int16')- 128)
        #data = np.abs(data[0:int(self.CHUNK / 2)]) / 10
        data = np.abs(data[0:int(CHUNK)]) / 100
        i = 0
        while i < 1024:
            data[i] = data[i] * i * 0.001
            i += 1
        x = []
        y = []
        t = 0
        n = 0
        f = 0
        while(t <= 2):
            x.append(self.pos + (self.radius + data[n]) * np.cos(np.pi * f))
            y.append(self.pos + (self.radius + data[n]) * np.sin(np.pi * f))
            n += 1
            t += self.increments
            if n < 50:
                f += self.increments * 8
            elif n < 100:
                f += self.increments * 4
            elif n < 200:
                f += self.increments * 2.05
            elif n < 400:
                f += self.increments * 0.61
            elif n < 700:
                f += self.increments * 0.25
            else:
                f += self.increments * 0.10
                
        x[0] = x[-1]
        y[0] = y[-1]
        cart_pair = (x, y)
        cart_pair = self.smoothing(x, y)
        return cart_pair
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from CircleMovement import SpectrumMovement, WaveMovement

import struct
from pyaudio import PyAudio, paFloat32, paInt16
from scipy.fftpack import fft

import sys
import time



class SoundCircle(object):

    def __init__(self):
        pg.setConfigOptions(antialias=True)
        self.app = QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title='SoundCircle')
        self.win.setWindowTitle('SoundCircle')
        self.win.setGeometry(0, 0, 1920, 1080)

        #Adding circles to our dict
        self.circles = {SpectrumMovement(61, (10,100,10), 98) : [None, None],
                        #WaveMovement(54, (130,0,0), 95) : [None, None],
                        #WaveMovement(47, (190,0,0), 92) : [None, None],
                        #WaveMovement(40, (250,0,0), 89) : [None, None],
        }
        # and assigning PlotItems, the actual graphical circles
        for c in self.circles:
            self.circles[c][0] = self.win.addPlot(
            row=1, col=1, axisItems={}
            )
            self.circles[c][0].hideAxis('left')
            self.circles[c][0].hideAxis('bottom')

        #self.win.showMaximized()
        self.win.showFullScreen()


        #PyAudio setup
        self.FORMAT = paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024 * 2

        self.p = PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=False,
            frames_per_buffer=self.CHUNK,
        )


    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()


    def plot_data(self, circ, data_x, data_y):
        if circ.first_draw:
            #The first time we draw the circle, we set its properties
            the_line = self.circles[circ][0].plot(pen=circ.color, width=300)
            self.circles[circ][1] = the_line
            self.circles[circ][0].setYRange(0, 200, padding=0)
            self.circles[circ][0].setXRange(-90, 270, padding=0)
            circ.first_draw = False
        else:
            #Here we just update the data for each circle
            self.circles[circ][1].setData(data_x, data_y)

    def update_all(self):
        in_data = self.stream.read(self.CHUNK)
        for circle in self.circles:
            plot_tuple = circle.update(in_data, self.CHUNK)
            self.plot_data(circle, plot_tuple[0], plot_tuple[1])

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update_all)
        timer.start(20)
        self.start()

    
if __name__ == '__main__':
    app = SoundCircle()
    app.animation()






'''x.append(self.pos + (self.radius) * np.cos(np.pi * t)  + rnd)
    y.append(self.pos + (self.radius) * np.sin(np.pi * t)  + rnd)
^ Makes a 3D cylinder'''
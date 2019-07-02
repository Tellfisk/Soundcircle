'''Credits to Mark Jay 
https://github.com/markjay4k/Audio-Spectrum-Analyzer-in-Python/blob/master/audio_spectrumQT.py
for coding about everything in this file. I've only contributed with some minor changes to make 
it work as I intend
'''
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import struct
from pyaudio import PyAudio, paFloat32, paInt16
from scipy.fftpack import fft

import sys
import time


class WaveformSpectrum(object):
    def __init__(self):

        # pyqtgraph stuff
        pg.setConfigOptions(antialias=True)
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title='Spectrum Analyzer')
        self.win.setWindowTitle('Spectrum Analyzer')
        self.win.setGeometry(5, 115, 1910, 1070)

        wf_xlabels = []
        wf_xaxis = pg.AxisItem(orientation='bottom')
        wf_xaxis.setTicks([wf_xlabels])

        wf_ylabels = [(128, '')]
        wf_yaxis = pg.AxisItem(orientation='left')
        wf_yaxis.setTicks([wf_ylabels])

        sp_xlabels = [
            (np.log10(20), '20'), (np.log10(50), '50'), (np.log10(100), '100'),
            (np.log10(200), '200'), (np.log10(500), '500'), (np.log10(1000), '1000'), 
            (np.log10(2000), '2000'), (np.log10(5000), '5000'), (np.log10(10000), '10000'),
            (np.log10(15000), '15000'), (np.log10(20000), '20000')
        ]
        sp_xaxis = pg.AxisItem(orientation='bottom')
        sp_xaxis.setTicks([sp_xlabels])

        sp_ylabels = [
            (-0.675, '-0.0dB'), (-0.85, '-3.0dB'), (-1.05, '-6.0dB'), 
            (-1.16, '-9.0dB'), (-1.28, '-12.0dB')
        ]
        sp_yaxis = pg.AxisItem(orientation='left')
        sp_yaxis.setTicks([sp_ylabels])

        self.waveform = self.win.addPlot(
            #title='WAVEFORM', 
            row=1, col=1, axisItems={'bottom': wf_xaxis, 'left': wf_yaxis},
        )
        self.spectrum = self.win.addPlot(
            #title='SPECTRUM', 
            row=2, col=1, axisItems={'bottom': sp_xaxis, 'left': sp_yaxis},
        )

        # pyaudio stuff
        self.FORMAT = paInt16
        #self.FORMAT = paFloat32
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
        # waveform and spectrum x points
        self.x = np.arange(0, 2 * self.CHUNK, 2)
        self.f = np.linspace(0, self.RATE / 2, self.CHUNK / 2)

        # Init for smoothing
        self.sp_prev_chunk = [-1] * int(self.CHUNK/2)

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, data_x, data_y):
        if name in self.traces:
            self.traces[name].setData(data_x, data_y)
        else:
            if name == 'waveform':
                self.traces[name] = self.waveform.plot(pen='c', width=3)
                self.waveform.setYRange(0, 255, padding=0) 
                self.waveform.setXRange(0, 2 * self.CHUNK, padding=0.005)
            if name == 'spectrum':
                self.traces[name] = self.spectrum.plot(pen='m', width=3)
                self.spectrum.setLogMode(x=True, y=True)
                self.spectrum.setYRange(-3.60, -0.675, padding=0)
                self.spectrum.setXRange(
                    np.log10(20), np.log10(self.RATE / 2), padding=0.005)

    def update(self):
        wf_data = self.stream.read(self.CHUNK)
        wf_data = np.frombuffer(wf_data, dtype='h')
        wf_data = np.array(wf_data, dtype='h')/140 + 255
        ''' ^ Had to increase dtype from 'b' to 'h', scale down (/140) and remove slicing of array'''
        self.set_plotdata(name='waveform', data_x=self.x, data_y=wf_data-128)

        sp_data = fft(np.array(wf_data, dtype='int16')- 128)   ###Data[0] might be relativily extremely large 
        sp_data = np.abs(sp_data[0:int(self.CHUNK / 2)]) / (256 * self.CHUNK)
        sp_data = self.smoothing(sp_data)
        self.set_plotdata(name='spectrum', data_x=self.f, data_y=sp_data)

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()

    def smoothing(self, new_array):
        assert len(new_array) == len(self.sp_prev_chunk), "Chunks of different size!"
        tmp_array = []
        for i in range(len(new_array)):
            tmp_array.append((new_array[i] + self.sp_prev_chunk[i]) / 2)     #Smooth
            #tmp_array.append((new_array[i] + self.sp_prev_chunk[i]*4) / 5)  #Smoother
        self.sp_prev_chunk = tmp_array
        return tmp_array

if __name__ == '__main__':
    audio_app = WaveformSpectrum()
    audio_app.animation()
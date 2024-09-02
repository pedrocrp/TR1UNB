import numpy as np
from scipy.fftpack import fft, fftfreq

class CamadaFisicaReceptora:
    def __init__(self):
        pass

    def nrz_polar_decode(self, signal):
        """ Decode Non-return to Zero Polar encoded signal """
        return ''.join(['1' if voltage > 0 else '0' for voltage in signal])


    def manchester_decode(self, signal):
        """ Decode Manchester encoded signal """
        decoded = []
        for i in range(0, len(signal), 2):
            if signal[i] == 1 and signal[i+1] == -1:
                decoded.append('1')
            elif signal[i] == -1 and signal[i+1] == 1:
                decoded.append('0')
        return ''.join(decoded)


    def bipolar_decode(self, signal):
        """ Decode Bipolar encoded signal """
        decoded = []
        last_voltage = 0
        for voltage in signal:
            if voltage == 0:
                decoded.append('0')
            elif voltage != last_voltage:
                decoded.append('1')
            last_voltage = voltage
        return ''.join(decoded)

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

    def ask_decode(self, signal, threshold=2.5):
        """ Decode Amplitude Shift Keying signal """
        return ''.join(['1' if amplitude >= threshold else '0' for amplitude in signal])

    def fsk_decode(self, signal, freq_high=2, freq_low=1, sample_rate=100):
        """ Decode Frequency Shift Keying signal """
        n = len(signal)
        t = np.linspace(0, n / sample_rate, n, endpoint=False)
        yf = fft(signal)
        xf = fftfreq(n, 1 / sample_rate)
        
        decoded = []
        chunk_size = sample_rate  # assuming one bit per second for simplicity
        for i in range(0, len(signal), chunk_size):
            chunk_fft = np.abs(yf[i:i+chunk_size])
            dominant_freq = xf[np.argmax(chunk_fft)]
            if np.isclose(dominant_freq, freq_high, atol=0.1):
                decoded.append('1')
            elif np.isclose(dominant_freq, freq_low, atol=0.1):
                decoded.append('0')
        return ''.join(decoded)

    def qam_decode(self, signal, mapping=None):
        """ Decode 8-QAM signal """
        if mapping is None:
            mapping = {
                '000': (-1, -1),
                '001': (-1, 0),
                '010': (-1, 1),
                '011': (0, 1),
                '100': (1, 1),
                '101': (1, 0),
                '110': (1, -1),
                '111': (0, -1)
            }
        decoded = []
        for amplitude, phase in signal:
            min_distance = float('inf')
            closest_bits = None
            for bits, (ref_amplitude, ref_phase) in mapping.items():
                distance = (ref_amplitude - amplitude)**2 + (ref_phase - phase)**2
                if distance < min_distance:
                    min_distance = distance
                    closest_bits = bits
            decoded.append(closest_bits)
        return ''.join(decoded)

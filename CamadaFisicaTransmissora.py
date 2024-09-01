import numpy as np

class CamadaFisicaTransmissora:
    def __init__(self):
        pass

    def nrz_polar(self, bit_string):
        """ Non-return to Zero Polar encoding """
        self.validate_bit_string(bit_string)
        return [1 if bit == '1' else -1 for bit in bit_string]

    def manchester(self, bit_string):
        """ Manchester encoding """
        self.validate_bit_string(bit_string)
        encoded = []
        for bit in bit_string:
            if bit == '1':
                encoded.extend([1, -1])  # High to low transition
            else:
                encoded.extend([-1, 1])  # Low to high transition
        return encoded

    def bipolar(self, bit_string):
        """ Bipolar encoding """
        self.validate_bit_string(bit_string)
        voltage = 1
        encoded = []
        for bit in bit_string:
            if bit == '1':
                encoded.append(voltage)
                voltage *= -1  # Flip the voltage for the next '1'
            else:
                encoded.append(0)  # '0' is always 0 voltage
        return encoded

    def ask(self, bit_string, amplitude_high=3, freq_carrier=10, freq_pulse=2, duration=1, sample_rate=1000):
        """ Amplitude Shift Keying with carrier and pulse frequency """
        self.validate_bit_string(bit_string)

        t = np.arange(0, duration, 1/sample_rate)
        carrier_wave = amplitude_high * np.sin(2 * np.pi * freq_carrier * t)
        
        # Generate the pulse (square wave) based on the bit_string
        pulse_wave = np.zeros_like(t)
        bit_duration = duration / len(bit_string)
        for i, bit in enumerate(bit_string):
            start_idx = int(i * bit_duration * sample_rate)
            end_idx = int((i + 1) * bit_duration * sample_rate)
            pulse_wave[start_idx:end_idx] = 1 if bit == '1' else 0

        # ASK modulated signal
        ask_signal = carrier_wave * pulse_wave

        return ask_signal

    def fsk(self, bit_string, freq_high=2, freq_low=1, duration=1, sample_rate=100):
        """ Frequency Shift Keying """
        self.validate_bit_string(bit_string)
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        encoded = []
        for bit in bit_string:
            frequency = freq_high if bit == '1' else freq_low
            encoded_signal = np.sin(2 * np.pi * frequency * t)
            encoded.extend(encoded_signal)
        return np.array(encoded)

    def qam(self, bit_string):
        """ 8-Quadrature Amplitude Modulation """
        self.validate_bit_string(bit_string)
        # Mapping for 8-QAM, assuming Gray coding for simplification
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
        encoded = []
        for i in range(0, len(bit_string), 3):
            bits = bit_string[i:i+3]
            if len(bits) < 3:
                bits = bits.ljust(3, '0')  # Padding if necessary
            encoded.append(mapping[bits])
        return encoded
    
    def validate_bit_string(self, bit_string):
        """ Validate the bit string input. """
        if any(bit not in '01' for bit in bit_string):
            raise ValueError("Invalid bit string. Only '0' and '1' are allowed.")

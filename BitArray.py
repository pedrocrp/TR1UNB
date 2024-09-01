class BitArray:
    def __init__(self, data):
        if isinstance(data, str):
            self.bits = [int(bit) for bit in ''.join(format(ord(c), '08b') for c in data)]
        elif isinstance(data,list) and all([isinstance(x, int) for x in data]):
            self.bits = data
        else:
            raise TypeError("Data can't be converted to BitArray.")

    def tam(self):
        return len(self.bits)

    def setBit(self, index):
        self.bits[index] = 1

    def clearBit(self, index):
        self.bits[index] = 0

    def print(self):
        return (''.join(map(str, self.bits)))

    def toString(self):
        chars = [chr(int(''.join(map(str, self.bits[i:i+8])), 2)) for i in range(0, len(self.bits), 8)]
        return ''.join(chars)

    def __getitem__(self, index):
        return self.bits[index]

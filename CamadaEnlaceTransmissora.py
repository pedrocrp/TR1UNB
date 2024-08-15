class CamadaEnlaceTransmissora:
    def __init__(self):
        pass

    #maxFrame em bits, calculado a partir de um valor em bytes

    #minFrame = 16 (count, payload)
    def byteCount(self, maxFrameSize, bit_array):
        """ byte count framing """
        if maxFrameSize % 8:
            raise(ValueError("Tamanho máximo de quadro inválido."))
        #max count = 0b11111111
        maxFrameSize = max(maxFrameSize,256 + 8)
        #one byte for count
        frameCount = (bit_array.tam() // (maxFrameSize - 8)) + 1
        frames = []
        for i in range(frameCount):
            payload = bit_array.bits[i * (maxFrameSize - 8):(i + 1) * (maxFrameSize - 8)]
            frames.extend([int(bit) for bit in format(len(payload)//8, '08b')])
            frames.extend(payload)
        return frames

    #minFrame = 32 (flag, esc, payload, flag)
    def charInsert(self, maxFrameSize, bit_array):
        """ byte flag insertion framing """
        if maxFrameSize % 8:
            raise(ValueError("Tamanho máximo de quadro inválido."))
        start = 0
        frames = []
        flag = [0,0,0,0,1,0,0,1]
        esc = [0,0,0,1,1,0,1,1]
        while start < bit_array.tam():
            payload = []
            #two bytes for flags
            while len(payload) < maxFrameSize - 16 and start < bit_array.tam():
                byte = bit_array.bits[start:start + 8]
                if byte not in [flag, esc]:
                    payload.extend(byte)
                #one more byte for esc
                elif len(payload) < maxFrameSize - 24:
                    payload.extend(esc)
                    payload.extend(byte)
                else:
                    break
                start += 8
            frames.extend(flag)
            frames.extend(payload)
            frames.extend(flag)
        return frames
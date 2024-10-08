from BitArray import BitArray

class CamadaEnlaceTransmissora:
    def __init__(self,detectionCorrection):
        self.detection = []
        self.detectionSize = 0
        for n in detectionCorrection:
            match n:
                case "Paridade":
                    self.detection.append(self.parityBit)
                    self.detectionSize += 8
                case "CRC-32":
                    self.detection.append(self.crc32)
                    self.detectionSize += 32
                case "Nenhum":
                    self.detection.append(lambda x:x)
        self.correction = "Hamming" in detectionCorrection
        self.hammingBits = 0

    def byteCount(self, maxFrameSize, bit_array, frameStacks, stackedFraming):
        """ byte count framing """
        realMaxFrameSize = maxFrameSize
        maxFrameSize -= sum([x[1] for x in frameStacks])
        if maxFrameSize % 8:
            raise(ValueError("Tamanho máximo de quadro inválido."))
        #max count = 0b11111111
        maxFrameSize = min(maxFrameSize,256)
        #one byte for count
        maxFrameSize =  maxFrameSize - 8
        if self.correction and not stackedFraming:
            #correction limits message size
            maxFrameSize = self.hamming(maxFrameSize)
        if not stackedFraming:
            payloadSize = maxFrameSize - self.detectionSize
        else:
            payloadSize = maxFrameSize
        nFrames = bit_array.tam() / payloadSize
        nFrames = int(nFrames) if nFrames == int(nFrames) else int(nFrames) + 1
        frame = []
        frames = []
        for i in range(nFrames):
            payload = bit_array.bits[i * (payloadSize):(i + 1) * (payloadSize)]
            if not stackedFraming:
                for detection in self.detection:
                    payload = detection(payload)
                if self.correction:
                    payload = self.hamming(payload)
            frame.extend([int(bit) for bit in format(len(payload)//8, '08b')])
            frame.extend(payload)
            if frameStacks:
                frameAlg = frameStacks[0][0]
                frame = frameAlg(realMaxFrameSize,BitArray(frame),frameStacks[1:],True)
            frames.extend(frame)
            frame = []
        return frames

    def charInsert(self, maxFrameSize, bit_array, frameStacks, stackedFraming):
        """ byte flag insertion framing """
        realMaxFrameSize = maxFrameSize
        maxFrameSize -= sum([x[1] for x in frameStacks])
        if maxFrameSize % 8:
            raise(ValueError("Tamanho máximo de quadro inválido."))
        start = 0
        frame = []
        frames = []
        #flag = unicode tab, esc = unicode esc
        flag = [0,0,0,0,1,0,0,1]
        esc = [0,0,0,1,1,0,1,1]
        #two bytes for flags
        maxFrameSize =  maxFrameSize - 16
        if self.correction and not stackedFraming:
            #correction limits message size
            maxFrameSize = self.hamming(maxFrameSize)
        if not stackedFraming:
            maxPayloadSize = maxFrameSize - self.detectionSize
            #could be needed to escape all detection and correction bytes
            maxPayloadSize -= ((self.hammingBits // 8)+(self.detectionSize // 8)) * 8
        else:
            maxPayloadSize = maxFrameSize
        while start < bit_array.tam():
            payload = []
            payloadSize = maxPayloadSize
            while len(payload) < payloadSize and start < bit_array.tam():
                byte = bit_array.bits[start:start + 8]
                if byte not in [flag, esc]:
                    payload.extend(byte)
                #one more byte for esc
                elif len(payload) < payloadSize - 8:
                    payloadSize -= 8
                    payload.extend(byte)
                else:
                    break
                start += 8
            if not stackedFraming:
                for detection in self.detection:
                    payload = detection(payload)
                if self.correction:
                    payload = self.hamming(payload)
            i = 0
            escaped = []
            while i < len(payload):
                if payload[i:i + 8] in [flag,esc]:
                    escaped.extend(esc + payload[i:i + 8])
                else:
                    escaped.extend(payload[i:i + 8])
                i += 8
            frame.extend(flag)
            frame.extend(escaped)
            frame.extend(flag)
            if frameStacks:
                frameAlg = frameStacks[0][0]
                frame = frameAlg(realMaxFrameSize,BitArray(frame),frameStacks[1:],True)
            frames.extend(frame)
            frame = []
        return frames

    def parityBit(self,bit_list):
        """ error detection via interleaved bit parity """
        #one bit for each 12,5% of message, one byte added to message
        for i in range(8):
            column = [bit_list[j + i] for j in range(0, len(bit_list) - 7, 8)]
            bit_list.append(column.count(1) % 2)
        return bit_list

    def crc32(self,data):
        """error detection via crc-32 IEEE 802.3 """
        # CRC-32 IEEE polynomial
        polynomial = 0x82608EDB
        crc = 0x00000000
        #allocate remainder space before calculation
        for bit in data + [0 for i in range(31)]:
            crc = (crc << 1) | bit
            if crc & 0x80000000:
                crc ^= polynomial
        #remainder gets padded with zero so its length is exactly 4 bytes
        crc_bit_string = bin(crc)[2:].zfill(32)
        crc_bit_list = [int(bit) for bit in crc_bit_string]
        return data + crc_bit_list

    def hamming(self,data):
        """ errors detection and one bit errors correction via hamming code """
        #data is maxbits in frame
        if isinstance(data,int):
            ones = data.bit_count()
            #hamming bits; if data is a power of 2, one bit is discarded
            self.hammingBits = data.bit_length() - (1 if ones == 1 else 0)
            #how many bits can be used for bytes of data
            return ((data - self.hammingBits) // 8) * 8
        #data is bitarray
        hamming = [0 for i in range(self.hammingBits)]
        i, h_i = 0, 1
        while i < len(data):
            #hamming index is a power of 2
            if h_i.bit_count() == 1:
                h_i += 1
            #hamming_index points to a data bit
            else:
                for j in range(len(hamming)):
                    if (2 ** j) & h_i:
                        hamming[j] ^= data[i]
                i, h_i = i + 1, h_i + 1
        data.extend(hamming)
        #pad result so its length is an exact number of bytes
        data.extend([0 for i in range((-len(data)) % 8)])
        return data
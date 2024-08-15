class CamadaEnlaceReceptora:
    def __init__(self):
        pass

    def byteCountParse(self, bit_array):
        """ parse frame with byte count """
        i = 0
        message = []
        while i < bit_array.tam():
            frameSize = int(''.join(map(str,bit_array.bits[i:i + 8])),2)
            message.extend(bit_array.bits[i + 8:i + 8 + (frameSize * 8)])
            i += 8 + (frameSize * 8)
        return message

    def charInsertParse(self, bit_array):
        """ parse frame with flags """
        start = 0
        message = []
        flag = [0,0,0,0,1,0,0,1]
        esc = [0,0,0,1,1,0,1,1]
        started, escaped = False, False
        while start < bit_array.tam():
            byte = bit_array.bits[start:start + 8]
            if byte == flag and not started:
                started = True
            elif started and byte == esc and not escaped:
                escaped = True
            elif started and (byte not in [esc,flag] or escaped):
                message.extend(byte)
                escaped = False
            elif started and byte == flag and not escaped:
                started = False
            else:
                raise ValueError("Erro em enquadramento.")
            start += 8
        return message
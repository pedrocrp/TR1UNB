class CamadaEnlaceReceptora:
    def __init__(self,detection,correction):
        match detection:
            case 1:
                self.detection = self.parityBitCheck
                self.detectionSize = 8
            case 2:
                self.detection = self.crc32Check
                self.detectionSize = 32
            case 3:
                self.detection = lambda x:(True,x)
                self.detectionSize = 0
        self.correction = correction

    def byteCountParse(self, bit_array):
        """ parse frame with byte count """
        i, f = 0, 1
        message = []
        while i < bit_array.tam():
            frameSize = int(''.join(map(str,bit_array.bits[i:i + 8])),2)
            frame = bit_array.bits[i + 8:i + 8 + (frameSize * 8)]
            if self.correction:
                frame = self.hammingCheck(frame)
            check, checked = self.detection(frame)
            print(f"Quadro {f}:" , "correto." if check else "com erro.")
            f += 1
            message.extend(checked)
            i += 8 + (frameSize * 8)
        return message

    def charInsertParse(self, bit_array):
        """ parse frame with flags """
        start, f = 0, 1
        message, frame = [], []
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
                frame.extend(byte)
                escaped = False
            elif started and byte == flag and not escaped:
                started = False
                if self.correction:
                    frame = self.hammingCheck(frame)
                check, checked = self.detection(frame)
                print(f"Quadro {f}:" , "correto." if check else "com erro.")
                f += 1
                message.extend(checked)
                frame = []
            else:
                print(f"Quadro {f}: Erro em enquadramento.")
                while byte != flag:
                    start += 8
                    byte = bit_array.bits[start:start + 8]
                if bit_array.bits[start + 8:start + 16] == flag:
                    start += 8
                f += 1
                continue
            start += 8
        return message

    def parityBitCheck(self,bit_list):
        """ check if an error happened with parity bits"""
        parity = bit_list[-8:]
        check = []
        for i in range(8):
            column = [bit_list[j + i] for j in range(0, len(bit_list) - 15, 8)]
            check.append(column.count(1) % 2)
        return parity == check, bit_list[:-8]

    def crc32Check(self,data):
        """ check if an error happened with crc-32 IEEE 802.3 """
        # CRC-32 IEEE polynomial
        polynomial = 0x82608EDB
        crc = 0x00000000
        #remove padding bit
        for bit in data[:-32] + data[-31:]:
            crc = (crc << 1) | bit
            if crc & 0x80000000:
                crc ^= polynomial
        crc_bit_string = bin(crc)[2:].zfill(31)
        crc_bit_list = [int(bit) for bit in crc_bit_string]
        return crc_bit_list == [0 for i in range(31)], data[:-32]

    def hammingCheck(self,data):
        """ check for errors and correct one bit errors with hamming code """
        ones = len(data).bit_count()
        #hamming bits; if len(data) is a power of 2, one bit is discarded
        hammingBits = len(data).bit_length() - (1 if ones == 1 else 0)
        #hamming bits + number of bits to make an exact number of bytes
        hammingPlusPad = hammingBits + ((-hammingBits) % 8)
        hamming = data[-hammingPlusPad:][:hammingBits]
        data = data[:-hammingPlusPad]
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
        if hamming.count(1) > 1:
            hamming = int(''.join(map(str,hamming[::-1])),2)
            hamming = hamming - (hamming.bit_length() + 1)
            if hamming < len(data):
                print("Quadro corrigido.")
                data[hamming] ^= 1
            else:
                print("Erro em dois ou mais bits detectado no quadro.")
        return data
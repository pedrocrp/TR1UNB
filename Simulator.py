import random
from BitArray import BitArray
from CamadaFisicaReceptora import CamadaFisicaReceptora
from CamadaFisicaTransmissora import CamadaFisicaTransmissora
from CamadaEnlaceReceptora import CamadaEnlaceReceptora
from CamadaEnlaceTransmissora import CamadaEnlaceTransmissora

class Simulacao:
    def __init__(self, tipoCodificacao, tipoPortadora, tipoEnquadramento, tipoDeteccaoCorrecao, maxTamQuadro, chanceErro):
        self.dict_information = {}
        self.fisicaTransmissora = CamadaFisicaTransmissora()
        self.fisicaReceptora = CamadaFisicaReceptora()

        match tipoCodificacao:
            case "Manchester": # Manchester
                self.encode = self.fisicaTransmissora.manchester
                self.decode = self.fisicaReceptora.manchester_decode
            case "Bipolar": # Bipolar
                self.encode = self.fisicaTransmissora.bipolar
                self.decode = self.fisicaReceptora.bipolar_decode
            case "NRZ-Polar": # NRZ-Polar
                self.encode = self.fisicaTransmissora.nrz_polar
                self.decode = self.fisicaReceptora.nrz_polar_decode

        match tipoPortadora:

            case "ASK": # ASK
                self.encode_portadora = self.fisicaTransmissora.ask
                self.decode_portadora = self.fisicaReceptora.ask_decode
            case "FSK": # FSK
                self.encode_portadora = self.fisicaTransmissora.fsk
                self.decode_portadora = self.fisicaReceptora.fsk_decode
            case "QAM": # QAM
                self.encode_portadora = self.fisicaTransmissora.qam
                self.decode_portadora = self.fisicaReceptora.qam_decode

        self.tamanhoMinQuadro = 8 #one byte

        for n in tipoDeteccaoCorrecao:
            match n:
                case "Paridade":
                    #8 parity bits
                    self.tamanhoMinQuadro += 8
                case "CRC-32":
                    #31 bits for crc32 remainder + 1 padding bit
                    self.tamanhoMinQuadro += 32
                case "Nenhum":
                    #no checking
                    pass
                case "Hamming":
                    ones = self.tamanhoMinQuadro.bit_count()
                    #hamming bits; if minlength is a power of 2, one bit is discarded
                    hammingBits = self.tamanhoMinQuadro.bit_length() - (1 if ones == 1 else 0)
                    #pad hammming bits to a length in bytes
                    if hammingBits % 8 != 0:
                        self.tamanhoMinQuadro += hammingBits + (8 - (hammingBits % 8))
                    else:
                        self.tamanhoMinQuadro += hammingBits
        self.enlaceTransmissora = CamadaEnlaceTransmissora(tipoDeteccaoCorrecao)
        self.enlaceReceptora = CamadaEnlaceReceptora(tipoDeteccaoCorrecao[::-1])
        self.frame, self.frameparse = [], []
        for n in tipoEnquadramento:
            match n:
                case "Contagem de Bytes": #bytecount
                    self.frame.append((self.enlaceTransmissora.byteCount, 8))
                    self.frameparse.insert(0,self.enlaceReceptora.byteCountParse)
                    #byte with frame size
                    self.tamanhoMinQuadro += 8
                case "Inserção de Caracteres": #char insert
                    self.frame.append((self.enlaceTransmissora.charInsert,16 + self.tamanhoMinQuadro))
                    self.frameparse.insert(0,self.enlaceReceptora.charInsertParse)
                    #flags + extreme case where all bytes in frame need to be escaped
                    self.tamanhoMinQuadro += 16 + self.tamanhoMinQuadro
        if self.frame == [] or self.frameparse == []:
            raise ValueError("Tipo de enquadramento não foi provido.")

        self.tamanhoMaxQuadro = maxTamQuadro * 8
        if self.tamanhoMaxQuadro < self.tamanhoMinQuadro:
            raise ValueError("Tamanho de quadro insuficiente para transmissão com os parâmetros escolhidos. Não é possível estabelecer comunicação.")
        self.probabilidadeErro = chanceErro


    def run_simulator(self, mensagem):
        self.mensagem_original = self.camadaDeAplicacaoTransmissora(mensagem)
        self.quadros_enlace_transmissora = self.camadaEnlaceTransmissora(self.mensagem_original)
        self.fluxoBrutoDeBits_transmissora = self.camadaFisicaTransmissora(BitArray(self.quadros_enlace_transmissora))
        self.fluxoBrutoDeBitsPontoB = self.meioDeComunicacao(self.fluxoBrutoDeBits_transmissora)
        self.fluxoBrutoDeBits_receptora = self.camadaFisicaReceptora(self.fluxoBrutoDeBitsPontoB)
        self.quadros_enlace_receptora =  self.camadaEnlaceReceptora(self.fluxoBrutoDeBits_receptora)


    def camadaDeAplicacaoTransmissora(self, mensagem):
        mensagem = BitArray(mensagem)
        return mensagem


    def camadaEnlaceTransmissora(self,mensagem):
        frameAlg = self.frame.pop(0)[0]
        quadros = frameAlg(self.tamanhoMaxQuadro,mensagem,self.frame,False)
        return quadros


    def camadaFisicaTransmissora(self, quadro):
        fluxoBrutoDeBits = self.encode(''.join(map(str, quadro.bits)))
        return fluxoBrutoDeBits


    def meioDeComunicacao(self, fluxoBrutoDeBits):
        tamQuadro = len(fluxoBrutoDeBits)
        fluxoBrutoDeBitsPontoB = [0] * tamQuadro
        for i in range(tamQuadro):
            bit = fluxoBrutoDeBits[i]
            if random.random() > (self.probabilidadeErro / 100.0):
                fluxoBrutoDeBitsPontoB[i] = bit
            else:
                if isinstance(bit, tuple):
                    # Inverta a fase e a amplitude para simular erro
                    fluxoBrutoDeBitsPontoB[i] = (-bit[0], -bit[1])
                else:
                    fluxoBrutoDeBitsPontoB[i] = -bit if bit != 0 else 1
        return fluxoBrutoDeBitsPontoB


    def camadaFisicaReceptora(self, fluxoBrutoDeBitsPontoB):
        fluxoBrutoDeBits = self.decode(fluxoBrutoDeBitsPontoB)
        return BitArray([int(bit) for bit in fluxoBrutoDeBits])


    def camadaEnlaceReceptora(self,quadros):
        frameParseAlg = self.frameparse.pop(0)
        quadros = frameParseAlg(quadros,self.frameparse,self.frameparse != [])
        return BitArray(quadros)
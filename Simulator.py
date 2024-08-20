import random
from CamadaFisicaReceptora import CamadaFisicaReceptora
from CamadaFisicaTransmissora import CamadaFisicaTransmissora
from CamadaEnlaceReceptora import CamadaEnlaceReceptora
from CamadaEnlaceTransmissora import CamadaEnlaceTransmissora

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
        print(''.join(map(str, self.bits)))

    def toString(self):
        chars = [chr(int(''.join(map(str, self.bits[i:i+8])), 2)) for i in range(0, len(self.bits), 8)]
        return ''.join(chars)

    def __getitem__(self, index):
        return self.bits[index]


class Simulacao:
    def __init__(self, tipoCodificacao, tipoEnquadramento, tipoDeteccaoErro, correcao, maxTamQuadro, chanceErro):
        self.fisicaTransmissora = CamadaFisicaTransmissora()
        self.fisicaReceptora = CamadaFisicaReceptora()
        match tipoCodificacao:
            case 1: # Manchester
                self.encode = self.fisicaTransmissora.manchester
                self.decode = self.fisicaReceptora.manchester_decode
            case 2: # Bipolar
                self.encode = self.fisicaTransmissora.bipolar
                self.decode = self.fisicaReceptora.bipolar_decode
            case 3: # ASK
                self.encode = self.fisicaTransmissora.ask
                self.decode = self.fisicaReceptora.ask_decode
            case 4: # FSK
                self.encode = self.fisicaTransmissora.fsk
                self.decode = self.fisicaReceptora.fsk_decode
            case 5: # QAM
                self.encode = self.fisicaTransmissora.qam
                self.decode = self.fisicaReceptora.qam_decode
            case 6: # NRZ-Polar
                self.encode = self.fisicaTransmissora.nrz_polar
                self.decode = self.fisicaReceptora.nrz_polar_decode
            case _:
                raise ValueError("Tipo de codificação inválido. Escolha um valor entre 1 e 6.")
        match tipoDeteccaoErro:
            case 1:
                self.enlaceTransmissora = CamadaEnlaceTransmissora(1,correcao)
                self.enlaceReceptora = CamadaEnlaceReceptora(1,correcao)
                #3 bytes: message, 8 parity bits and 5 hamming bits (padded to a byte)
                self.tamanhoMinQuadro = 24
            case 2:
                self.enlaceTransmissora = CamadaEnlaceTransmissora(2,correcao)
                self.enlaceReceptora = CamadaEnlaceReceptora(2,correcao)
                #6 bytes: message, 31 bits for crc32 remainder + 1 padding bit and 7 hamming bits (padded to a byte)
                self.tamanhoMinQuadro = 48
            case 3:
                self.enlaceTransmissora = CamadaEnlaceTransmissora(3,correcao)
                self.enlaceReceptora = CamadaEnlaceReceptora(3,correcao)
                #2 bytes: message and 3 hamming bits (padded to a byte)
                self.tamanhoMinQuadro = 16
            case _:
                raise ValueError("Tipo de detecção de erro inválido. Escolha um valor entre 1 e 3.")
        match tipoEnquadramento:
            case 1: #bytecount
                self.frame = self.enlaceTransmissora.byteCount
                self.frameparse = self.enlaceReceptora.byteCountParse
                #byte with frame size
                self.tamanhoMinQuadro += 8
            case 2: #char insert
                self.frame = self.enlaceTransmissora.charInsert
                self.frameparse = self.enlaceReceptora.charInsertParse
                #flags + extreme case where all bytes in frame need to be escaped
                self.tamanhoMinQuadro += 16 + self.tamanhoMinQuadro
            case _:
                raise ValueError("Tipo de enquadramento inválido. Escolha 1 ou 2.")


        self.tamanhoMaxQuadro = maxTamQuadro * 8
        if self.tamanhoMaxQuadro < self.tamanhoMinQuadro:
            raise ValueError("Tamanho de quadro insuficiente para transmissão com os parâmetros escolhidos. Não é possível estabelecer comunicação.")
        self.probabilidadeErro = chanceErro

    def camadaDeAplicacaoTransmissora(self, mensagem):
        mensagem = BitArray(mensagem)
        print("\nMensagem original: ", end='')
        mensagem.print()
        self.camadaEnlaceTransmissora(mensagem)

    def camadaEnlaceTransmissora(self,mensagem):
        quadros = self.frame(self.tamanhoMaxQuadro,mensagem)
        self.camadaFisicaTransmissora(BitArray(quadros))

    def camadaFisicaTransmissora(self, quadro):
        fluxoBrutoDeBits = self.encode(''.join(map(str, quadro.bits)))
        self.meioDeComunicacao(fluxoBrutoDeBits)

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
        self.camadaFisicaReceptora(fluxoBrutoDeBitsPontoB)


    def camadaFisicaReceptora(self, fluxoBrutoDeBitsPontoB):
        fluxoBrutoDeBits = self.decode(fluxoBrutoDeBitsPontoB)
        self.camadaEnlaceReceptora(BitArray([int(bit) for bit in fluxoBrutoDeBits]))

    def camadaEnlaceReceptora(self,quadros):
        quadros = self.frameparse(quadros)
        self.camadaDeAplicacaoReceptora(BitArray(quadros))

    def camadaDeAplicacaoReceptora(self, mensagem):
        print("A mensagem recebida foi:", mensagem.toString())

simulacao = Simulacao(tipoCodificacao=6, tipoEnquadramento=2, tipoDeteccaoErro=1, correcao = True, maxTamQuadro=15, chanceErro=0)
simulacao.camadaDeAplicacaoTransmissora("Boa noi\x09teeee\x1bbeeeee ééééé")
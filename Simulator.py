import random
import time
from CamadaFisicaReceptora import CamadaFisicaReceptora
from CamadaFisicaTransmissora import CamadaFisicaTransmissora

class BitArray:
    def __init__(self, data):
        if isinstance(data, str):
            self.bits = [int(bit) for bit in ''.join(format(ord(c), '08b') for c in data)]
        else:
            self.bits = data

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
    def __init__(self, tipoCodificacao, chanceErro, seed=None):
        if tipoCodificacao == 1:
            self.fisicaTransmissora = CamadaFisicaTransmissora()  # Manchester
            self.fisicaReceptora = CamadaFisicaReceptora()
            self.encode = self.fisicaTransmissora.manchester
            self.decode = self.fisicaReceptora.manchester_decode
        elif tipoCodificacao == 2:
            self.fisicaTransmissora = CamadaFisicaTransmissora()  # Bipolar
            self.fisicaReceptora = CamadaFisicaReceptora()
            self.encode = self.fisicaTransmissora.bipolar
            self.decode = self.fisicaReceptora.bipolar_decode
        elif tipoCodificacao == 3:
            self.fisicaTransmissora = CamadaFisicaTransmissora()  # ASK
            self.fisicaReceptora = CamadaFisicaReceptora()
            self.encode = self.fisicaTransmissora.ask
            self.decode = self.fisicaReceptora.ask_decode
        elif tipoCodificacao == 4:
            self.fisicaTransmissora = CamadaFisicaTransmissora()  # FSK
            self.fisicaReceptora = CamadaFisicaReceptora()
            self.encode = self.fisicaTransmissora.fsk
            self.decode = self.fisicaReceptora.fsk_decode
        elif tipoCodificacao == 5:
            self.fisicaTransmissora = CamadaFisicaTransmissora()  # QAM
            self.fisicaReceptora = CamadaFisicaReceptora()
            self.encode = self.fisicaTransmissora.qam
            self.decode = self.fisicaReceptora.qam_decode
        elif tipoCodificacao == 6:
            self.fisicaTransmissora = CamadaFisicaTransmissora()  # NRZ-Polar
            self.fisicaReceptora = CamadaFisicaReceptora()
            self.encode = self.fisicaTransmissora.nrz_polar
            self.decode = self.fisicaReceptora.nrz_polar_decode
        else:
            raise ValueError("Tipo de codificação inválido. Escolha um valor entre 1 e 6.")

        self.probabilidadeErro = chanceErro

    def camadaDeAplicacaoTransmissora(self, mensagem):
        quadro = BitArray(mensagem)
        print("\nMensagem original: ", end='')
        quadro.print()
        self.camadaFisicaTransmissora(quadro)

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
        self.camadaDeAplicacaoReceptora(BitArray([int(bit) for bit in fluxoBrutoDeBits]))

    def camadaDeAplicacaoReceptora(self, fluxoBrutoDeBits):
        mensagem = fluxoBrutoDeBits.toString()
        print("A mensagem recebida foi:", mensagem)

simulacao = Simulacao(tipoCodificacao=6, chanceErro=0, seed=42)
simulacao.camadaDeAplicacaoTransmissora("Boa noiteeeeeeeee ééééé")
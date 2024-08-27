import random
from BitArray import BitArray
from CamadaFisicaReceptora import CamadaFisicaReceptora
from CamadaFisicaTransmissora import CamadaFisicaTransmissora
from CamadaEnlaceReceptora import CamadaEnlaceReceptora
from CamadaEnlaceTransmissora import CamadaEnlaceTransmissora

class Simulacao:
    def __init__(self, tipoCodificacao, tipoEnquadramento, tipoDeteccaoCorrecao, maxTamQuadro, chanceErro):
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
        self.tamanhoMinQuadro = 8 #one byte
        for n in tipoDeteccaoCorrecao:
            match n:
                case 1:
                    #8 parity bits
                    self.tamanhoMinQuadro += 8
                case 2:
                    #31 bits for crc32 remainder + 1 padding bit
                    self.tamanhoMinQuadro += 32
                case 3:
                    #no checking
                    pass
                case 4:
                    ones = self.tamanhoMinQuadro.bit_count()
                    #hamming bits; if minlength is a power of 2, one bit is discarded
                    hammingBits = self.tamanhoMinQuadro.bit_length() - (1 if ones == 1 else 0)
                    #pad hammming bits to a length in bytes
                    if hammingBits % 8 != 0:
                        self.tamanhoMinQuadro += hammingBits + (8 - (hammingBits % 8))
                    else:
                        self.tamanhoMinQuadro += hammingBits
                case _:
                    raise ValueError("Tipo de detecção e/ou correção de erro inválido. Escolha um valor entre 1 e 4.")
        self.enlaceTransmissora = CamadaEnlaceTransmissora(tipoDeteccaoCorrecao)
        self.enlaceReceptora = CamadaEnlaceReceptora(tipoDeteccaoCorrecao[::-1])
        self.frame, self.frameparse = [], []
        for n in tipoEnquadramento:
            match n:
                case 1: #bytecount
                    self.frame.append((self.enlaceTransmissora.byteCount, 8))
                    self.frameparse.insert(0,self.enlaceReceptora.byteCountParse)
                    #byte with frame size
                    self.tamanhoMinQuadro += 8
                case 2: #char insert
                    self.frame.append((self.enlaceTransmissora.charInsert,16 + self.tamanhoMinQuadro))
                    self.frameparse.insert(0,self.enlaceReceptora.charInsertParse)
                    #flags + extreme case where all bytes in frame need to be escaped
                    self.tamanhoMinQuadro += 16 + self.tamanhoMinQuadro
                case _:
                    raise ValueError("Tipo de enquadramento inválido. Escolha 1 ou 2.")
        if self.frame == [] or self.frameparse == []:
            raise ValueError("Tipo de enquadramento não foi provido.")

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
        frameAlg = self.frame.pop(0)[0]
        quadros = frameAlg(self.tamanhoMaxQuadro,mensagem,self.frame,False)
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
        frameParseAlg = self.frameparse.pop(0)
        quadros = frameParseAlg(quadros,self.frameparse,self.frameparse != [])
        self.camadaDeAplicacaoReceptora(BitArray(quadros))

    def camadaDeAplicacaoReceptora(self, mensagem):
        print("A mensagem recebida foi:", mensagem.toString())

simulacao = Simulacao(tipoCodificacao=6, tipoEnquadramento=[2,1,2,1], tipoDeteccaoCorrecao = [1,2,3,3,2], maxTamQuadro=56, chanceErro=0)
simulacao.camadaDeAplicacaoTransmissora("Boa noi\x09teeee\x1bbeeeee ééééé")
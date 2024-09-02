import numpy as np

class CamadaFisicaTransmissora:
    def __init__(self):
        pass


    def nrz_polar(self, bit_string):
        """ 
        Implementa a codificação Non-Return to Zero Polar (NRZ-P).

        Parâmetros:
        - bit_string: string que contém a sequência de bits a ser codificada (composta por '0's e '1's)

        Retorna:
        - Uma lista de valores onde '1' é representado por +1 e '0' é representado por -1
        """

        self.validate_bit_string(bit_string)  # Verifica se a string de bits é válida.
        return [1 if bit == '1' else -1 for bit in bit_string]  # Codifica cada bit como +1 ou -1


    def manchester(self, bit_string):
        """ 
        Implementa a codificação Manchester.

        Parâmetros:
        - bit_string: string que contém a sequência de bits a ser codificada.

        Retorna:
        - Uma lista de valores codificados, onde cada bit é representado por uma transição:
          '1' é codificado como [1, -1] (transição de alto para baixo) e
          '0' como [-1, 1] (transição de baixo para alto).
        """
        self.validate_bit_string(bit_string)  # Verifica se a string de bits é válida.
        encoded = []
        for bit in bit_string:
            if bit == '1':
                encoded.extend([1, -1])  # Transição de alto para baixo para o bit '1'.
            else:
                encoded.extend([-1, 1])  # Transição de baixo para alto para o bit '0'.
        return encoded  # Retorna a lista de valores codificados.


    def bipolar(self, bit_string):
        """ 
        Implementa a codificação Bipolar.

        Parâmetros:
        - bit_string: string que contém a sequência de bits a ser codificada.

        Retorna:
        - Uma lista de valores onde '1' alterna entre +1 e -1, e '0' é sempre representado por 0.
        """
        self.validate_bit_string(bit_string)  # Verifica se a string de bits é válida.
        voltage = 1
        encoded = []
        for bit in bit_string:
            if bit == '1':
                encoded.append(voltage)  # Aplica a voltagem corrente para o bit '1'.
                voltage *= -1  # Inverte a voltagem para o próximo '1'.
            else:
                encoded.append(0)  # '0' é sempre representado por 0.
        return encoded  # Retorna a lista de valores codificados.


    def ask(self, bit_string, A=1, f=5, sample_rate=100):
        """
        Realiza a modulação ASK (Amplitude Shift Keying) em uma string de bits.

        Parâmetros:
        bit_string (str): String de bits a ser modulada.
        A (float): Amplitude da onda portadora (padrão 1).
        f (float): Frequência da onda portadora (padrão 5 Hz).
        sample_rate (int): Taxa de amostragem, ou número de amostras por bit (padrão 100).

        Retorna:
        np.ndarray: Sinal modulado em ASK, limitado aos primeiros 10 bits.
        """
        
        self.validate_bit_string(bit_string)  # Valida a string de bits
        
        sig_size = len(bit_string)  # Determina o número de bits na string
        signal = np.zeros(sig_size * sample_rate)  # Inicializa o array do sinal com zeros, alocando memória para todo o sinal

        # Loop para cada bit na string
        for i in range(sig_size):
            if bit_string[i] == '1':
                # Se o bit é '1', gera uma onda senoidal com amplitude A e frequência f
                for j in range(sample_rate):
                    signal[(i * sample_rate) + j] = A * np.sin(2 * np.pi * f * (j + 1) / sample_rate)
            else:
                # Se o bit é '0', mantém o sinal em zero para o intervalo correspondente
                for j in range(sample_rate):
                    signal[(i * sample_rate) + j] = 0
        
        # Retorna o sinal ASK modulado, limitado aos primeiros 10 bits
        return signal[:10 * sample_rate]


    def fsk(self, bit_string, A=1, f1=5, f2=2, sample_rate=1000):
        """
        Realiza a modulação FSK (Frequency Shift Keying) em uma string de bits.

        Parâmetros:
        bit_string (str): String de bits a ser modulada.
        A (float): Amplitude da onda portadora (padrão 1).
        f1 (float): Frequência da portadora para o bit '1' (padrão 5 Hz).
        f2 (float): Frequência da portadora para o bit '0' (padrão 2 Hz).
        sample_rate (int): Taxa de amostragem, ou número de amostras por segundo (padrão 1000).

        Retorna:
        np.ndarray: Sinal modulado em FSK, limitado aos primeiros 10 bits.
        """
        
        self.validate_bit_string(bit_string)  # Valida a string de bits
        
        sig_size = len(bit_string)  # Tamanho do sinal, equivalente ao número de bits na string
        signal = np.zeros(sig_size * sample_rate)  # Inicializa o array do sinal com zeros

        # Loop para cada bit na string
        for i in range(sig_size):
            # Determina a frequência a ser usada com base no valor do bit
            if bit_string[i] == '1':
                frequency = f1
            else:
                frequency = f2

            # Gera a onda senoidal para o bit atual e armazena no sinal
            for j in range(sample_rate):
                signal[i * sample_rate + j] = A * np.sin(2 * np.pi * frequency * (j + 1) / sample_rate)
        
        # Retorna o sinal FSK modulado, limitado aos primeiros 10 bits
        return signal[:10 * sample_rate]


    def qam(self, bit_string, num_symbols = 8): # Para 8-QAM, temos 8 símbolos na constelação
        """
        Realiza a modulação 8-QAM (8-Quadrature Amplitude Modulation) em uma string de bits (Porém é possível modificar o valor de num_symbos
        para outros valores por exemplo 16-qam)

        Parâmetros:
        bit_string (str): String de bits a ser modulada.

        Retorna:
        np.ndarray: Sinal modulado em 8-QAM como uma matriz de números complexos
        """
        
        self.validate_bit_string(bit_string)  # Valida a string de bits
        
        num_bits_per_symbol = int(np.log2(num_symbols))  # Cada símbolo é representado por 3 bits (log2(8) = 3)

        # Faz o padding (adiciona 0's no final para que a quantidade de bits seja múltiplo de 3)
        if len(bit_string) % num_bits_per_symbol != 0:
            padding_length = num_bits_per_symbol - (len(bit_string) % num_bits_per_symbol)
            bit_string += '0' * padding_length

        sqrt_num_symbols = int(np.sqrt(num_symbols))  # A raiz quadrada do número de símbolos, define os eixos I e Q

        # Gera a constelação Gray para os componentes I (In-phase) e Q (Quadrature)
        bit_vector = np.arange(sqrt_num_symbols)

        # Converte os números binários presentes em bit_vector para seus equivalentes em código Gray
        gray_constellation = np.bitwise_xor(bit_vector, np.floor(bit_vector/2).astype(int))


        # Define as posições possíveis dos símbolos I e Q na constelação
        odd_numbers = np.arange(1, sqrt_num_symbols * 2, 2)  # Gera uma sequência de números ímpares
        symbol_positions = np.concatenate((np.flip(-odd_numbers, axis=0), odd_numbers)).astype(int)

        # Converte a string de bits em um array de bits e, em seguida, divide em grupos de 3 bits
        data_bits = np.array([int(bit) for bit in bit_string]).reshape((-1, num_bits_per_symbol))
        
        # Inicializa os componentes I e Q com zeros
        in_phase_component = np.zeros((data_bits.shape[0],))
        quadrature_component = np.zeros((data_bits.shape[0],))
        
        # Calcula o componente In-phase (I) a partir dos primeiros bits de cada símbolo
        for n in range(int(data_bits.shape[1] / 2)):
            in_phase_component += data_bits[:, n] * 2 ** n
        
        # Calcula o componente Quadrature (Q) a partir dos bits restantes de cada símbolo
        for n in range(int(data_bits.shape[1] / 2), int(data_bits.shape[1])):
            quadrature_component += data_bits[:, n] * 2 ** (n - int(data_bits.shape[1] / 2))
        
        # Converte os componentes I e Q para inteiros
        in_phase_component = in_phase_component.astype(int)
        quadrature_component = quadrature_component.astype(int)
        
        # Aplica a codificação Gray, se especificado
        in_phase_component = gray_constellation[in_phase_component % sqrt_num_symbols]
        quadrature_component = gray_constellation[quadrature_component % sqrt_num_symbols]

        # Mapeia os componentes I e Q para suas respectivas posições na constelação
        in_phase_component = symbol_positions[in_phase_component % len(symbol_positions)]
        quadrature_component = symbol_positions[quadrature_component % len(symbol_positions)]

        # Gera o sinal QAM modulado como uma combinação de componentes I e Q (números complexos)
        modulated_signal = in_phase_component + 1j * quadrature_component

        return modulated_signal  # Retorna o sinal modulado como números complexos
    
    
    
    def validate_bit_string(self, bit_string):
        """ Validate the bit string input. """
        if any(bit not in '01' for bit in bit_string):
            raise ValueError("Invalid bit string. Only '0' and '1' are allowed.")

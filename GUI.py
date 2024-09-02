import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.interpolate import UnivariateSpline

# Importar as classes necessárias
from CamadaFisicaTransmissora import CamadaFisicaTransmissora
from CamadaFisicaReceptora import CamadaFisicaReceptora
from CamadaEnlaceTransmissora import CamadaEnlaceTransmissora
from CamadaEnlaceReceptora import CamadaEnlaceReceptora
from Simulator import Simulacao

class SimulacaoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulação de Codificação e Modulação")
        ctk.set_appearance_mode("dark")  # Modo escuro
        ctk.set_default_color_theme("blue")  # Tema azul

        # Definindo as variáveis
        self.tipoCodificacaoDigital = ctk.StringVar(value="NRZ-Polar")
        self.tipoCodificacaoPortadora = ctk.StringVar(value="ASK")
        self.enquadramento = ["Contagem de Bytes"]
        self.deteccao = []
        self.hamming = None
        self.maxTamQuadro = ctk.IntVar(value=12)
        self.chanceErro = ctk.DoubleVar(value=0.4)
        self.mensagem = ctk.StringVar(value="Bom dia, turma de TR1!")
        self.caixasErro = {}
        self.caixasQuadros = {}
        self.fig = None
        self.fig2 = None

        # Layout esquerdo para os campos
        left_frame = ctk.CTkFrame(self.root)
        left_frame.pack(side=ctk.LEFT, padx=10, pady=10)

        # Dropdowns e entradas
        ctk.CTkLabel(left_frame, text="Codificação Digital:").pack(anchor=ctk.W)
        ctk.CTkOptionMenu(left_frame, variable=self.tipoCodificacaoDigital, values=["NRZ-Polar", "Manchester", "Bipolar"]).pack(fill=ctk.X)

        ctk.CTkLabel(left_frame, text="Codificação da Portadora:").pack(anchor=ctk.W)
        ctk.CTkOptionMenu(left_frame, variable=self.tipoCodificacaoPortadora, values=["ASK", "FSK", "QAM"]).pack(fill=ctk.X)

        ctk.CTkLabel(left_frame, text="Enquadramento:").pack(anchor=ctk.W)
        ctgBytesVar = ctk.StringVar(left_frame,value="Contagem de Bytes")
        ctgBytesCheckBox = ctk.CTkCheckBox(left_frame, text="1 - Contagem de Bytes", command=lambda :self.checkboxQuadros(ctgBytesVar,"Contagem de Bytes"),variable=ctgBytesVar, onvalue="Contagem de Bytes", offvalue="")
        charInsertVar = ctk.StringVar(left_frame,value="")
        charInsertCheckBox = ctk.CTkCheckBox(left_frame, text="Inserção de Caracteres", command=lambda :self.checkboxQuadros(charInsertVar,"Inserção de Caracteres"),variable=charInsertVar, onvalue="Inserção de Caracteres", offvalue="")
        self.caixasQuadros = {"Contagem de Bytes":ctgBytesCheckBox,"Inserção de Caracteres":charInsertCheckBox}
        ctgBytesCheckBox.pack(fill=ctk.X)
        charInsertCheckBox.pack(fill=ctk.X)

        ctk.CTkLabel(left_frame, text="Detecção de Erros:").pack(anchor=ctk.W)
        paridadeVar = ctk.StringVar(left_frame,value="")
        paridadeCheckBox = ctk.CTkCheckBox(left_frame, text="Paridade", command=lambda :self.checkboxErros(paridadeVar,"Paridade"),variable=paridadeVar, onvalue="Paridade", offvalue="")
        crcVar = ctk.StringVar(left_frame,value="")
        crcCheckBox = ctk.CTkCheckBox(left_frame, text="CRC-32", command=lambda :self.checkboxErros(crcVar,"CRC-32"),variable=crcVar, onvalue="CRC-32", offvalue="")
        self.caixasErro = {"Paridade":paridadeCheckBox,"CRC-32":crcCheckBox}
        paridadeCheckBox.pack(fill=ctk.X)
        crcCheckBox.pack(fill=ctk.X)

        ctk.CTkLabel(left_frame, text="Correção de Erros:").pack(anchor=ctk.W)
        #ctk.CTkOptionMenu(left_frame, variable=self.tipoCorrecaoErro, values=["Nenhum", "Hamming"]).pack(fill=ctk.X)
        self.hamming = ctk.StringVar(left_frame,value="")
        hammingCheckBox = ctk.CTkCheckBox(left_frame, text="Hamming",variable=self.hamming, onvalue="Hamming", offvalue="")
        hammingCheckBox.pack(fill=ctk.X)

        ctk.CTkLabel(left_frame, text="Tamanho Máximo do Quadro:").pack(anchor=ctk.W)
        ctk.CTkEntry(left_frame, textvariable=self.maxTamQuadro).pack(fill=ctk.X)

        ctk.CTkLabel(left_frame, text="Porcentagem de Erro:").pack(anchor=ctk.W)
        ctk.CTkEntry(left_frame, textvariable=self.chanceErro).pack(fill=ctk.X)

        ctk.CTkLabel(left_frame, text="Mensagem:").pack(anchor=ctk.W)
        ctk.CTkEntry(left_frame, textvariable=self.mensagem).pack(fill=ctk.X)

        # Botão para executar a simulação
        ctk.CTkButton(left_frame, text="Executar Simulação", command=self.executar_simulacao).pack(pady=10)

        # Layout direito para resultados
        right_frame = ctk.CTkFrame(self.root)
        right_frame.pack(side=ctk.LEFT, padx=10, pady=10, fill=ctk.BOTH, expand=True)

        self.resultado_texto = ctk.CTkTextbox(right_frame, height=100)
        self.resultado_texto.pack(fill=ctk.BOTH, expand=True)

        self.canvas_frame = ctk.CTkFrame(right_frame)
        self.canvas_frame.pack(fill=ctk.BOTH, expand=True)


    def checkboxQuadros(self,w,opcao):
        if w.get() != '':
            self.enquadramento.append(w.get())
            self.caixasQuadros[w.get()].configure(text=f"2 - {w.get()}")
        else:
            if len(self.enquadramento) == 1:
                w.set(opcao)
            else:
                self.enquadramento.remove(opcao)
                self.caixasQuadros[opcao].configure(text=f"{opcao}")
                self.caixasQuadros[self.enquadramento[0]].configure(text=f"1 - {self.enquadramento[0]}")


    def checkboxErros(self,w,opcao):
        if w.get() != '':
            self.deteccao.append(w.get())
            self.caixasErro[w.get()].configure(text=f"{len(self.deteccao)} - {w.get()}")
        else:
            self.deteccao.remove(opcao)
            self.caixasErro[opcao].configure(text=f"{opcao}")
            for i in range(len(self.deteccao)):
                self.caixasErro[self.deteccao[i]].configure(text=f"{i + 1} - {self.deteccao[i]}")



    def texto_para_binario(self, texto,):
        return ''.join(format(ord(c), '08b') for c in texto)


    def executar_simulacao(self):
        # Coletando as variáveis
        tipo_digital = self.tipoCodificacaoDigital.get()
        tipo_portadora = self.tipoCodificacaoPortadora.get()
        #enquadramento = self.tipoEnquadramento.get()
        deteccao = self.deteccao if self.deteccao else ["Nenhum"]
        correcao = self.hamming.get()
        deteccaoCorrecao = [*self.deteccao,correcao] if correcao else deteccao
        max_quadro = self.maxTamQuadro.get()
        erro = self.chanceErro.get()
        mensagem = self.mensagem.get()


        try:
            simulacao = Simulacao(tipoCodificacao= tipo_digital,
                                tipoPortadora= tipo_portadora,
                                tipoEnquadramento=self.enquadramento,
                                tipoDeteccaoCorrecao = deteccaoCorrecao,
                                maxTamQuadro=max_quadro,
                                chanceErro=erro)
        except ValueError as e:
            self.resultado_texto.delete("1.0", ctk.END)
            self.resultado_texto.insert(ctk.END, f"{e.args[0]}\n")
            return


        # Converter a mensagem de texto para binário
        mensagem_binaria = self.texto_para_binario(mensagem)

        # Criar uma instância da CamadaFisicaTransmissora para codificação
        fisicaTransmissora = CamadaFisicaTransmissora()

        if tipo_portadora == "ASK":
            modulated_signal = fisicaTransmissora.ask(mensagem_binaria)
        elif tipo_portadora == "FSK":
            modulated_signal = fisicaTransmissora.fsk(mensagem_binaria)
        elif tipo_portadora == "QAM":
            modulated_signal = fisicaTransmissora.qam(mensagem_binaria)

        simulacao.run_simulator(mensagem)

        log = []
        for msg, frames in simulacao.enlaceReceptora.log.items():
            if len(frames) > 1:
                log.append(f"{msg} Q{', Q'.join(sorted(map(str,frames)))}")
            elif len(frames) == 1:
                log.append(f"{msg} Q{frames.pop()}")

        # Exibir resultados
        self.resultado_texto.delete("1.0", ctk.END)
        self.resultado_texto.insert(ctk.END, f"Mensagem Original: {simulacao.mensagem_original.toString()}\n")
        self.resultado_texto.insert(ctk.END, f"Mensagem Binária: {mensagem_binaria}\n")
        self.resultado_texto.insert(ctk.END, f"Sinal Codificado ({tipo_digital}): {simulacao.fluxoBrutoDeBits_transmissora}\n")
        for msg in log:
            self.resultado_texto.insert(ctk.END, f"{msg}\n")
       
        msg_recebida = simulacao.quadros_enlace_receptora.toString()
     
        if msg_recebida:
            self.resultado_texto.insert(ctk.END, f"A mensagem recebida foi: {msg_recebida}\n")
        else:
            self.resultado_texto.insert(ctk.END, "Devido a erros, não foi possível decodificar os bits recebidos.\n")

        # Atualizar gráficos
        self.atualizar_graficos(simulacao.fluxoBrutoDeBits_transmissora, modulated_signal)

    def atualizar_graficos(self, encoded_signal, modulated_signal):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Gráfico do sinal codificado
        self.fig, ax = plt.subplots(figsize=(6, 4))
        # ax.step(range(len(encoded_signal)), encoded_signal, where='mid')
        ax.step(range(50), encoded_signal[:50], where='mid') # Diminuido o tamanho para ficar melhor de visualizar o gráfico
        ax.set_title("Sinal Codificado")
        ax.set_xlabel("Tempo")
        ax.set_ylabel("Amplitude")
        ax.legend()

        canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

        # Suavizando o sinal modulado
        x = np.arange(len(modulated_signal))
        spl = UnivariateSpline(x, modulated_signal, s=5)  
        modulated_signal_smooth = spl(x)

        # Gráfico do sinal modulado suavizado
        self.fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.plot(modulated_signal_smooth)
        ax2.set_title("Sinal Modulado")
        ax2.set_xlabel("Tempo")
        ax2.set_ylabel("Amplitude")
        ax2.legend()

        canvas2 = FigureCanvasTkAgg(self.fig2, master=self.canvas_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

        plt.close(self.fig)
        plt.close(self.fig2)

if __name__ == "__main__":
    root = ctk.CTk()
    app = SimulacaoApp(root)
    root.mainloop()

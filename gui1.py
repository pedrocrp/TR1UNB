import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Importar as classes necessárias
from CamadaFisicaTransmissora import CamadaFisicaTransmissora
from CamadaFisicaReceptora import CamadaFisicaReceptora
from CamadaEnlaceTransmissora import CamadaEnlaceTransmissora
from CamadaEnlaceReceptora import CamadaEnlaceReceptora

class SimulacaoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulação de Codificação e Modulação")
        ctk.set_appearance_mode("dark")  # Modo escuro
        ctk.set_default_color_theme("blue")  # Tema azul

        # Definindo as variáveis
        self.tipoCodificacaoDigital = ctk.StringVar(value="NRZ-Polar")
        self.tipoCodificacaoPortadora = ctk.StringVar(value="ASK")
        self.tipoEnquadramento = ctk.StringVar(value="Byte Count")
        self.tipoDeteccaoCorrecao = ctk.StringVar(value="Nenhum")
        self.tipoCorrecaoErro = ctk.StringVar(value="Nenhum")
        self.maxTamQuadro = ctk.IntVar(value=56)
        self.chanceErro = ctk.DoubleVar(value=0.0)
        self.mensagem = ctk.StringVar(value="oiii")

        # Layout esquerdo para os campos
        left_frame = ctk.CTkFrame(self.root)
        left_frame.pack(side=ctk.LEFT, padx=10, pady=10)

        # Dropdowns e entradas
        ctk.CTkLabel(left_frame, text="Codificação Digital:").pack(anchor=ctk.W)
        ctk.CTkOptionMenu(left_frame, variable=self.tipoCodificacaoDigital, values=["NRZ-Polar", "Manchester", "Bipolar"]).pack(fill=ctk.X)

        ctk.CTkLabel(left_frame, text="Codificação da Portadora:").pack(anchor=ctk.W)
        ctk.CTkOptionMenu(left_frame, variable=self.tipoCodificacaoPortadora, values=["ASK", "FSK", "QAM"]).pack(fill=ctk.X)

        ctk.CTkLabel(left_frame, text="Enquadramento:").pack(anchor=ctk.W)
        ctk.CTkOptionMenu(left_frame, variable=self.tipoEnquadramento, values=["Byte Count", "Inserção de Caracteres"]).pack(fill=ctk.X)

        ctk.CTkLabel(left_frame, text="Detecção de Erros:").pack(anchor=ctk.W)
        ctk.CTkOptionMenu(left_frame, variable=self.tipoDeteccaoCorrecao, values=["Nenhum", "Paridade", "CRC-32"]).pack(fill=ctk.X)

        ctk.CTkLabel(left_frame, text="Correção de Erros:").pack(anchor=ctk.W)
        ctk.CTkOptionMenu(left_frame, variable=self.tipoCorrecaoErro, values=["Nenhum", "Hamming"]).pack(fill=ctk.X)

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

    def texto_para_binario(self, texto):
        return ''.join(format(ord(c), '08b') for c in texto)

    def executar_simulacao(self):
        # Coletando as variáveis
        tipo_digital = self.tipoCodificacaoDigital.get()
        tipo_portadora = self.tipoCodificacaoPortadora.get()
        enquadramento = self.tipoEnquadramento.get()
        deteccao = self.tipoDeteccaoCorrecao.get()
        correcao = self.tipoCorrecaoErro.get()
        max_quadro = self.maxTamQuadro.get()
        erro = self.chanceErro.get()
        mensagem = self.mensagem.get()

        # Converter a mensagem de texto para binário
        mensagem_binaria = self.texto_para_binario(mensagem)

        # Criar uma instância da CamadaFisicaTransmissora para codificação
        fisicaTransmissora = CamadaFisicaTransmissora()

        # Selecionar a codificação digital e a modulação
        if tipo_digital == "NRZ-Polar":
            encoded_signal = fisicaTransmissora.nrz_polar(mensagem_binaria)
        elif tipo_digital == "Manchester":
            encoded_signal = fisicaTransmissora.manchester(mensagem_binaria)
        elif tipo_digital == "Bipolar":
            encoded_signal = fisicaTransmissora.bipolar(mensagem_binaria)

        if tipo_portadora == "ASK":
            modulated_signal = fisicaTransmissora.ask(mensagem_binaria)
        elif tipo_portadora == "FSK":
            modulated_signal = fisicaTransmissora.fsk(mensagem_binaria)
        elif tipo_portadora == "QAM":
            modulated_signal = fisicaTransmissora.qam(mensagem_binaria)

        # Exibir resultados
        self.resultado_texto.delete("1.0", ctk.END)
        self.resultado_texto.insert(ctk.END, f"Mensagem Original: {mensagem}\n")
        self.resultado_texto.insert(ctk.END, f"Mensagem Binária: {mensagem_binaria}\n")
        self.resultado_texto.insert(ctk.END, f"Sinal Codificado ({tipo_digital}): {encoded_signal}\n")

        # Atualizar gráficos
        self.atualizar_graficos(encoded_signal, modulated_signal)

    def atualizar_graficos(self, encoded_signal, modulated_signal):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Gráfico do sinal codificado
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.step(range(len(encoded_signal)), encoded_signal, where='mid', label="Sinal Codificado")
        ax.set_title("Sinal Codificado")
        ax.set_xlabel("Tempo")
        ax.set_ylabel("Amplitude")
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

        # Gráfico do sinal modulado
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.plot(modulated_signal, label="Sinal Modulado")
        ax2.set_title("Sinal Modulado")
        ax2.set_xlabel("Tempo")
        ax2.set_ylabel("Amplitude")
        ax2.legend()

        canvas2 = FigureCanvasTkAgg(fig2, master=self.canvas_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

if __name__ == "__main__":
    root = ctk.CTk()
    app = SimulacaoApp(root)
    root.mainloop()

import customtkinter

#Define tema e aparencia da interface
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")


#Inicializa e configura a interface
root = customtkinter.CTk()
root.title('TR1')
root.geometry("485x370")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)


#Declaracao das listas de opcoes utilizadas nos ComboBoxes
protocolosEnlace1a = ["Contagem", "Insercao"]
protocolosEnlace1b = ["Vazio", "Contagem", "Insercao"]
protocolosEnlace2 = ["Vazio", "Bit Paridade", "CRC", "Hamming"]

modulacaoDigital = ["Vazio", "NRZ-Polar", "Manchester", "Bipolar"]
modulacaoPortadora = ["Vazio", "ASK", "FSK", "8-QAM"]


#Funcao para pegar os valores escolhidos pelo usuario na interface
def choose_protocolos():
    lista_escolhidos = [enlace1.get(), enlace2.get(), enlace3.get(), enlace4.get(), fisicaDigital.get(), fisicaPortadora.get()]
    entrada_escolhida = entrada.get()
    erro_escolhido = int(slider.get())
    tamQuadro = entradaTamQuadro.get()
    #saida = lista_escolhidos
    #saida.append(entrada_escolhida)
    #saida.append(erro_escolhido)
    #saida.append(tamQuadro)
    #output_label.configure(text=saida)
    return lista_escolhidos, entrada_escolhida, erro_escolhido, tamQuadro

#Funcao para exibir o valor de erro definido no slider
def valor_slider(valor):
    labelSlider.configure(text=int(valor))

#Caixas de "entrada" de texto
entrada = customtkinter.CTkEntry(root,
    placeholder_text="Digite Sua Mensagem",
    width=185
    )
entrada.grid(column=0, row=0, pady=10, padx=10, columnspan=1)

entradaTamQuadro = customtkinter.CTkEntry(root,
    placeholder_text="Tamanho do quadro em bytes",
    width= 185
    )
entradaTamQuadro.grid(column=1, row=0, pady=10, padx=10, columnspan=1)


#Criando o frame de enlace
frameEnlace = customtkinter.CTkScrollableFrame(root, width=165)
frameEnlace.grid(row=1, column=1, padx=10, pady=(10,0), sticky="nsw")

labelEnlace = customtkinter.CTkLabel(frameEnlace,
    text="Protocolos de Enlace",
    font=("Helvetica", 12),
    fg_color="gray30",
    corner_radius=6
    )
labelEnlace.grid(row=0, column=0, padx=10, pady=10, sticky="enw")

#Criando as ComboBoxes para escolher os protocolos de enlace
enlace1 = customtkinter.CTkComboBox(frameEnlace, values=protocolosEnlace1a)
enlace1.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")

enlace2 = customtkinter.CTkComboBox(frameEnlace, values=protocolosEnlace1b)
enlace2.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")

enlace3 = customtkinter.CTkComboBox(frameEnlace, values=protocolosEnlace2)
enlace3.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")

enlace4 = customtkinter.CTkComboBox(frameEnlace, values=protocolosEnlace2)
enlace4.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="w")

enlace5 = customtkinter.CTkComboBox(frameEnlace, values=protocolosEnlace2)
enlace5.grid(row=5, column=0, padx=10, pady=(10, 0), sticky="w")


#Criando o frame da camada fisica
frameFisica = customtkinter.CTkScrollableFrame(root, width=235)
frameFisica.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsw")

#ComboBox e "titulo" de modulacao digital
labelFisicaDigital = customtkinter.CTkLabel(frameFisica,
    text="Digital",
    font=("Helvetica", 12),
    fg_color="gray30",
    corner_radius=6
    )
labelFisicaDigital.grid(row=0, column=0, padx=10, pady=10, sticky="enw")

fisicaDigital = customtkinter.CTkComboBox(frameFisica, values=modulacaoDigital)
fisicaDigital.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew")

#ComboBox e "titulo" de modulacao por portadora
labelFisicaPortadora = customtkinter.CTkLabel(frameFisica,
    text="Portadora",
    font=("Helvetica", 12),
    fg_color="gray30",
    corner_radius=6
    )
labelFisicaPortadora.grid(row=2, column=0, padx=10, pady=10, sticky="enw")

fisicaPortadora = customtkinter.CTkComboBox(frameFisica, values=modulacaoPortadora)
fisicaPortadora.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="ew")

#Titulo e slider para pegar a taxa de erro
labelFisicaErro = customtkinter.CTkLabel(frameFisica,
    text="Taxa de Erro",
    font=("Helvetica", 12),
    fg_color="gray30",
    corner_radius=6
    )
labelFisicaErro.grid(row=4, column=0, padx=10, pady=10, sticky="enw")

slider = customtkinter.CTkSlider(frameFisica, command=valor_slider, from_=0, to=100)
slider.grid(row=5, column=0, padx=(10, 10), pady=(10, 10), sticky="ns")

labelSlider = customtkinter.CTkLabel(frameFisica, text="", font=("Helvetica", 12))
labelSlider.grid(row=5, column=1, pady=10)


#Botao para confirmar os valores escolhidos
confirma_protocolo = customtkinter.CTkButton(root, text="Confirmar", command=choose_protocolos)
confirma_protocolo.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="s")

output_label = customtkinter.CTkLabel(master=root, text="", font=("Helvetica", 12))
output_label.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

root.mainloop()
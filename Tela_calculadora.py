import customtkinter as ctk
import math

def acao_do_botao():
    try:
        num1 = float(caixa_de_entrada1.get().strip())
        num2 = float(caixa_de_entrada2.get().strip())
        soma = num1 + num2
        rotulo_resultado.configure(text=f"A soma é: {soma}")
    except ValueError:
        rotulo_resultado.configure(text="Digite números válidos")
#----------------------------------------------------------------------------------
def subrair():
    try:
        num1 = float(caixa_de_entrada1.get().strip())
        num2 = float(caixa_de_entrada2.get().strip())
        subtracao = num1 - num2
        rotulo_resultado.configure(text=f"A subtraçao é: {subtracao}")
    except ValueError:
        rotulo_resultado.configure(text="Digite números válidos")
#----------------------------------------------------------------------------------
def limpar_tela():
    caixa_de_entrada1.delete(0, "end")
    caixa_de_entrada2.delete(0, "end")
    rotulo_resultado.configure(text="Aguardando o cálculo")
#----------------------------------------------------------------------------------
def multiplicar():
    try:
        num1 = float(caixa_de_entrada1.get().strip())
        num2 = float(caixa_de_entrada2.get().strip())
        produto = num1 * num2
        rotulo_resultado.configure(text=f"A multiplicação é: {produto}")
    except ValueError:
        rotulo_resultado.configure(text="Digite números válidos")
#----------------------------------------------------------------------------------
def dividir():
    try:
        num1 = float(caixa_de_entrada1.get().strip())
        num2 = float(caixa_de_entrada2.get().strip())
        if num2 == 0:
            rotulo_resultado.configure(text="Erro: Não pode ter divisão por zero")
        else:
            divisao = num1 / num2
            rotulo_resultado.configure(text=f"A divisão é: {divisao}")
    except ValueError:
        rotulo_resultado.configure(text="Digite números válidos")
#------------------------------------------------------------------------------------

def raiz_quadrada():
    try: 
        num1 = float(caixa_de_entrada1.get().strip()) 
        if num1 < 0: 
            rotulo_resultado.configure(text="Erro: Não existe raiz quadrada de número negativo")
        else:
            raiz= math.sqrt(num1)    
            rotulo_resultado.configure(text=f"A raiz é: {raiz}")
    except NameError:
        rotulo_resultado.configure(text="Digite números válidos")
#-------------------------------------------------------------------------------------------------------
def potenciacao():
    try:
        num1 = float(caixa_de_entrada1.get().strip())
        num2 = float(caixa_de_entrada2.get().strip())
        resultado = pow(num1,num2)
        rotulo_resultado.configure(text=f"A potencia é: {resultado}")
    except ValueError:
        rotulo_resultado.configure(text=f" Digite números validos")    
#------------------------------------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
#-----------------------------------------------------------------------------------
janela = ctk.CTk()
janela.title('Calculadora')
janela.geometry("500x450")
janela.configure(fg_color="black")  # fundo preto

#-----------------------------------------------------
titulo = ctk.CTkLabel(janela,
                      text="Bem-vindo à calculadora",
                      font=("Arial", 20, "bold"),
                      text_color="white")
titulo.grid(row=0, column=0, columnspan=2, pady=15)

#------------------------------------------------------------------------------------
caixa_de_entrada1 = ctk.CTkEntry(janela,
                                placeholder_text="Digite um número...",
                                width=250,
                                height=40,
                                font=("Arial",16),
                                corner_radius=20,
                                fg_color="transparent")
caixa_de_entrada1.grid(row=1, column=0, columnspan=2, pady=10)

#-------------------------------------------------------------------------------------
caixa_de_entrada2 = ctk.CTkEntry(janela,
                                placeholder_text="Digite um número...",
                                width=250,
                                height=40,
                                font=("Arial",16),
                                corner_radius=20,
                                fg_color="transparent")
caixa_de_entrada2.grid(row=2, column=0, columnspan=2, pady=10)
#----------------------------------------------------------------------------------------
caixa_do_frame = ctk.CTkFrame(janela)
caixa_do_frame.grid(row=3, column=0, columnspan=2, pady=10)
#---------------------------------------------------------------------------------------
#conifiguraçoes do botao de somar
botao = ctk.CTkButton(caixa_do_frame,
                    text="➕",
                    command=acao_do_botao,
                    width=120,
                    height=40,
                    corner_radius=20,
                    fg_color=("#4CAF50", "#2E7D32"),   
                    hover_color="#66BB6A")             
botao.grid(row=0, column=0, padx=5, pady=5)
#----------------------------------------------------------------------------------------
#conifiguraçoes do botao de subtrair
botao_subtrair = ctk.CTkButton(caixa_do_frame,
                    text="➖",
                    command=subrair,
                    width=120,
                    height=40,
                    corner_radius=20,
                    fg_color=("#FF7043", "#D84315"),   
                    hover_color="#FF8A65")
botao_subtrair.grid(row=0, column=3, padx=5, pady=5)
#----------------------------------------------------------------------------------------
#conifiguraçoes do botao de limpar a  tela
botao_limpar_tela = ctk.CTkButton(caixa_do_frame,
                    text="🗑️",
                    command=limpar_tela,
                    width=120,
                    height=40,
                    corner_radius=20,
                    fg_color=("#E53935", "#B71C1C"),  
                    hover_color="#EF5350")             
botao_limpar_tela.grid(row=0, column=1, padx=5, pady=5)
#----------------------------------------------------------------------------------------
#conifiguraçoes do botao de multiplicar
botao_multiplicar = ctk.CTkButton(caixa_do_frame,
                    text="✖️",
                    command=multiplicar,
                    width=120,
                    height=40,
                    corner_radius=20,
                    fg_color=("#42A5F5", "#1565C0"),   
                    hover_color="#64B5F6")
botao_multiplicar.grid(row=1, column=0, padx=5, pady=5)
#----------------------------------------------------------------------------------------
#conifiguraçoes do botao de dividir
botao_dividir = ctk.CTkButton(caixa_do_frame,
                    text="➗",
                    command=dividir,
                    width=120,
                    height=40,
                    corner_radius=20,
                    fg_color=("#AB47BC", "#6A1B9A"),  
                    hover_color="#BA68C8")
botao_dividir.grid(row=1, column=1, padx=5, pady=5)
#----------------------------------------------------------------------------------------
#conifiguraçoes do botao de raiz quadradada
botao_raiz = ctk.CTkButton(caixa_do_frame,
                    text="√",
                    command=raiz_quadrada,
                    width=120,
                    height=40,
                    corner_radius=20,
                    fg_color=("#FFCA28", "#F57F17"),   
                    hover_color="#FFD54F")
botao_raiz.grid(row=1, column=3, padx=5, pady=5)
#----------------------------------------------------------------------------------------
#conifiguraçoes do botao de potenciação
botao_potencia = ctk.CTkButton(caixa_do_frame,
                    text="^",
                    command=potenciacao,
                    width=120,
                    height=40,
                    corner_radius=20,
                    fg_color=("#26C6DA", "#00838F"),  
                    hover_color="#4DD0E1")
botao_potencia.grid(row=2, column=0, padx=5, pady=5)
#------------------------------------------------------------------------------------------
rotulo_resultado = ctk.CTkLabel(janela, 
                                text="Aguardando o cálculo", 
                                text_color="white",
                                font=("Arial", 16))
rotulo_resultado.grid(row=4, column=0, columnspan=2, pady=15)

janela.mainloop()

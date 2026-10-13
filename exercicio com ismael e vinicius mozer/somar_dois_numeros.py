import tkinter as tk
from tkinter import messagebox

def somar():
    try:
        # Busca os números digitados
        n1 = float(entry_num1.get())
        n2 = float(entry_num2.get())
        
        # Faz a soma e exibe na tela
        resultado = n1 + n2
        label_resultado.config(text=f"Resultado: {resultado:.2f}")
    except ValueError:
        messagebox.showerror("Erro", "Por favor, digite apenas números!")

# 1. Configuração Principal da Janela
janela = tk.Tk()
janela.title("Calculadora")
janela.geometry("350x300")
janela.configure(bg="#f4f4f9")  # Cor de fundo suave

# 2. Título da Tela
label_titulo = tk.Label(
    janela, 
    text="Calculadora de Soma", 
    font=("Arial", 16, "bold"), 
    bg="#f4f4f9", 
    fg="#333333"
)
label_titulo.pack(pady=20)

# 3. Campo de Entrada: Número 1
entry_num1 = tk.Entry(
    janela, 
    font=("Arial", 14), 
    justify="center", 
    bd=2, 
    relief="groove"
)
entry_num1.pack(pady=8, ipady=4)

# 4. Campo de Entrada: Número 2
entry_num2 = tk.Entry(
    janela, 
    font=("Arial", 14), 
    justify="center", 
    bd=2, 
    relief="groove"
)
entry_num2.pack(pady=8, ipady=4)

# 5. O Botão de Somar (Estilizado)
botao_somar = tk.Button(
    janela, 
    text="SOMAR (+)", 
    font=("Arial", 12, "bold"), 
    bg="#007BFF",      # Cor azul moderna
    fg="white",        # Texto branco
    activebackground="#0056b3", 
    activeforeground="white",
    cursor="hand2",    # Muda o mouse para a "mãozinha" ao passar por cima
    command=somar
)
botao_somar.pack(pady=15, ipadx=10, ipady=5)

# 6. Exibição do Resultado
label_resultado = tk.Label(
    janela, 
    text="Resultado: ", 
    font=("Arial", 14, "bold"), 
    bg="#f4f4f9", 
    fg="#28a745"       # Cor verde para o resultado
)
label_resultado.pack(pady=10)

# Mantém a janela aberta e rodando
janela.mainloop()
import tkinter as tk
from tkinter import messagebox

# Função para somar
def somar():
    try:
        n1 = float(entry_num1.get())
        n2 = float(entry_num2.get())
        resultado = n1 + n2
        label_resultado.config(text=f"Resultado: {resultado:.2f}", fg="#28a745") # Verde para soma
    except ValueError:
        messagebox.showerror("Erro", "Por favor, digite apenas números!")

# Função para subtrair
def subtrair():
    try:
        n1 = float(entry_num1.get())
        n2 = float(entry_num2.get())
        resultado = n1 - n2
        label_resultado.config(text=f"Resultado: {resultado:.2f}", fg="#dc3545") # Vermelho/Laranja para subtração
    except ValueError:
        messagebox.showerror("Erro", "Por favor, digite apenas números!")

# 1. Configuração Principal da Janela
janela = tk.Tk()
janela.title("Calculadora")
janela.geometry("350x320")
janela.configure(bg="#f4f4f9")

# 2. Título da Tela
label_titulo = tk.Label(
    janela, 
    text="Calculadora Simples", 
    font=("Arial", 16, "bold"), 
    bg="#f4f4f9", 
    fg="#333333"
)
label_titulo.pack(pady=20)

# 3. Campos de Entrada
entry_num1 = tk.Entry(janela, font=("Arial", 14), justify="center", bd=2, relief="groove")
entry_num1.pack(pady=8, ipady=4)

entry_num2 = tk.Entry(janela, font=("Arial", 14), justify="center", bd=2, relief="groove")
entry_num2.pack(pady=8, ipady=4)

# 4. Container (Frame) para colocar os botões lado a lado
frame_botoes = tk.Frame(janela, bg="#f4f4f9")
frame_botoes.pack(pady=15)

# Botão de Somar
botao_somar = tk.Button(
    frame_botoes, 
    text="SOMAR (+)", 
    font=("Arial", 11, "bold"), 
    bg="#007BFF",      # Azul
    fg="white",        
    cursor="hand2",    
    command=somar
)
botao_somar.pack(side="left", padx=10, ipadx=10, ipady=5)

# Botão de Subtrair
botao_subtrair = tk.Button(
    frame_botoes, 
    text="SUBTRAIR (-)", 
    font=("Arial", 11, "bold"), 
    bg="#6c757d",      # Cinza moderno
    fg="white",        
    cursor="hand2",    
    command=subtrair
)
botao_subtrair.pack(side="left", padx=10, ipadx=10, ipady=5)

# 5. Exibição do Resultado
label_resultado = tk.Label(
    janela, 
    text="Resultado: ", 
    font=("Arial", 14, "bold"), 
    bg="#f4f4f9", 
    fg="#333333"
)
label_resultado.pack(pady=15)

# Mantém a janela aberta
janela.mainloop()

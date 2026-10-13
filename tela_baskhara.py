import customtkinter as ctk
import math
def bhaskara():
     try: 
        a = float(caixa_de_entrada1.get().strip()) 
        b = float(caixa_de_entrada2.get().strip()) 
        c = float(caixa_de_entrada3.get().strip()) 

        delta = b**2 -4*a*c
        
        if delta < 0:
            rotulo_resultado.configure(text="Não existem raízes reais")

        else:
            x1 =(-b + math.sqrt(delta)) /(2*a)
            x2 =(-b - math.sqrt(delta)) /(2*a)
            rotulo_resultado.configure(text=f"As raizes são: x1= {x1} e {x2}")
     except ValueError:
         rotulo_resultado.configure(text="Digite números válidos")

#------------------------------------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
#-----------------------------------------------------------------------------------
janela = ctk.CTk()
janela.title('Calculadora')
janela.geometry("500x350")
janela.configure(fg_color="black")

caixa_de_entrada1 = ctk.CTkEntry(janela,
                                placeholder_text="Digite o valor de a...",
                                width=250,
                                height=40,
                                font=("Arial",16),
                                corner_radius=20,
                                fg_color="transparent")
caixa_de_entrada1.grid(row=1, column=0, columnspan=2, pady=10)
       
caixa_de_entrada2 = ctk.CTkEntry(janela,
                                placeholder_text="Digite o valor de b...",
                                width=250,
                                height=40,
                                font=("Arial",16),
                                corner_radius=20,
                                fg_color="transparent")
caixa_de_entrada2.grid(row=2, column=0, columnspan=2, pady=10)
       
caixa_de_entrada3 = ctk.CTkEntry(janela,
                                placeholder_text="Digite o valor de c...",
                                width=250,
                                height=40,
                                font=("Arial",16),
                                corner_radius=20,
                                fg_color="transparent")
caixa_de_entrada3.grid(row=3, column=0, columnspan=2, pady=10)

caixa_do_frame = ctk.CTkFrame(janela)
caixa_do_frame.grid(row=4, column=0, columnspan=2, pady=10)

botao_bhaskara = ctk.CTkButton(caixa_do_frame,
                    text="Bhaskara",
                    command=bhaskara,
                    width=120,
                    height=40,
                    corner_radius=20,
                    fg_color="orange")
botao_bhaskara.grid(row=2, column=1, padx=5, pady=5)
rotulo_resultado = ctk.CTkLabel(janela, 
                                text="Aguardando o cálculo", 
                                text_color="white",
                                font=("Arial", 16))
rotulo_resultado.grid(row=5, column=0, columnspan=2, pady=15)

janela.mainloop()
import customtkinter as ctk

def acao_do_botao():
    texto = caixa_de_entrada.get()
    texto2 = caixa_de_entrada2.get()
    rotulo_resultado.configure(text=texto)
    rotulo_resultado2.configure(text=texto2)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

janela = ctk.CTk()
janela.title('Mostrar nome e idade')
janela.geometry("500x500")

caixa_de_entrada = ctk.CTkEntry(janela,
                                placeholder_text="Digite seu nome...",
                                width=250,
                                height=30,
                                corner_radius=10,
                                fg_color="black")
caixa_de_entrada.pack(pady=10)
caixa_de_entrada2 = ctk.CTkEntry(janela,
                                placeholder_text="Digite sua idade...",
                                width=250,
                                height=30,
                                corner_radius=10,
                                fg_color="black")
caixa_de_entrada2.pack(pady=10)

botao = ctk.CTkButton(janela, text="Enviar", command=acao_do_botao)
botao.pack(pady=10)

rotulo_resultado = ctk.CTkLabel(janela, text="")
rotulo_resultado.pack(pady=10)

rotulo_resultado2 = ctk.CTkLabel(janela, text="")
rotulo_resultado2.pack(pady=10)

janela.mainloop()


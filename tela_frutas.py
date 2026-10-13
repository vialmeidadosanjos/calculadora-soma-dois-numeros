import customtkinter as ctk


frutas = [
    "maca",
    "banana",
    "laranja",
    "uva",
    "abacaxi",
    "manga",
    "pera",
    "morango",
    "kiwi",
    "melancia",
    "cereja",
    "pessego",
    "ameixa",
    "framboesa",
    "amora",
    "abacate",
    "coco",
    "figo",
    "goiaba",
    "jabuticaba",
    "maracuja",
]


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

janela = ctk.CTk()
janela.title("Exercicio de Listas")
janela.geometry("760x680")

quadro = ctk.CTkFrame(janela, fg_color="transparent")
quadro.pack(fill="both", expand=True, padx=16, pady=16)

titulo = ctk.CTkLabel(quadro, text="Lista de Frutas", font=("Arial", 28, "bold"))
titulo.pack(anchor="w", pady=(0, 4))

subtitulo = ctk.CTkLabel(
    quadro,
    text="Operacoes: pesquisar, adicionar, deletar e ordenar.",
    font=("Arial", 14),
)
subtitulo.pack(anchor="w", pady=(0, 12))

caixa_lista = ctk.CTkTextbox(quadro, width=700, height=260, font=("Consolas", 14))
caixa_lista.pack(fill="x", pady=(0, 12))
caixa_lista.configure(state="disabled")

mensagem = ctk.CTkLabel(quadro, text="", font=("Arial", 14))
mensagem.pack(anchor="w", pady=(0, 10))


linha_pesquisa = ctk.CTkFrame(quadro, fg_color="transparent")
linha_pesquisa.pack(fill="x", pady=4)

entrada_posicao_pesquisa = ctk.CTkEntry(
    linha_pesquisa,
    placeholder_text="Posicao para pesquisar",
    width=220,
)
entrada_posicao_pesquisa.pack(side="left", padx=(0, 8))


linha_adicionar = ctk.CTkFrame(quadro, fg_color="transparent")
linha_adicionar.pack(fill="x", pady=4)

entrada_nova_fruta = ctk.CTkEntry(linha_adicionar, placeholder_text="Nova fruta", width=220)
entrada_nova_fruta.pack(side="left", padx=(0, 8))


linha_deletar = ctk.CTkFrame(quadro, fg_color="transparent")
linha_deletar.pack(fill="x", pady=4)

entrada_posicao_deletar = ctk.CTkEntry(
    linha_deletar,
    placeholder_text="Posicao para deletar",
    width=220,
)
entrada_posicao_deletar.pack(side="left", padx=(0, 8))


linha_acoes = ctk.CTkFrame(quadro, fg_color="transparent")
linha_acoes.pack(fill="x", pady=(10, 0))


def atualizar_lista() -> None:
    linhas = [f"{i}: {fruta}" for i, fruta in enumerate(frutas)]
    caixa_lista.configure(state="normal")
    caixa_lista.delete("1.0", "end")
    caixa_lista.insert("1.0", "\n".join(linhas))
    caixa_lista.configure(state="disabled")


def pesquisar_fruta() -> None:
    texto = entrada_posicao_pesquisa.get().strip()
    try:
        posicao = int(texto)
    except ValueError:
        mensagem.configure(text="Digite uma posicao valida.")
        return

    if 0 <= posicao < len(frutas):
        mensagem.configure(text=f"A fruta na posicao {posicao} e: {frutas[posicao]}")
    else:
        mensagem.configure(text="Posicao invalida.")


def adicionar_fruta() -> None:
    nova = entrada_nova_fruta.get().strip()
    if not nova:
        mensagem.configure(text="Digite o nome da fruta para adicionar.")
        return

    frutas.append(nova)
    entrada_nova_fruta.delete(0, "end")
    mensagem.configure(text=f"Fruta '{nova}' adicionada.")
    atualizar_lista()


def deletar_fruta() -> None:
    texto = entrada_posicao_deletar.get().strip()
    try:
        posicao = int(texto)
    except ValueError:
        mensagem.configure(text="Digite uma posicao valida para deletar.")
        return

    if 0 <= posicao < len(frutas):
        removida = frutas[posicao]
        del frutas[posicao]
        entrada_posicao_deletar.delete(0, "end")
        mensagem.configure(text=f"Fruta '{removida}' removida.")
        atualizar_lista()
    else:
        mensagem.configure(text="Posicao invalida.")


def ordenar_frutas() -> None:
    frutas.sort()
    mensagem.configure(text="Lista ordenada em ordem alfabetica.")
    atualizar_lista()


botao_pesquisar = ctk.CTkButton(linha_pesquisa, text="Pesquisar", command=pesquisar_fruta)
botao_pesquisar.pack(side="left")

botao_adicionar = ctk.CTkButton(linha_adicionar, text="Adicionar", command=adicionar_fruta)
botao_adicionar.pack(side="left")

botao_deletar = ctk.CTkButton(linha_deletar, text="Deletar", command=deletar_fruta)
botao_deletar.pack(side="left")

botao_ordenar = ctk.CTkButton(linha_acoes, text="Ordenar A-Z", command=ordenar_frutas)
botao_ordenar.pack(side="left", padx=(0, 8))

botao_atualizar = ctk.CTkButton(linha_acoes, text="Atualizar Lista", command=atualizar_lista)
botao_atualizar.pack(side="left")

janela.bind("<Return>", lambda _event: pesquisar_fruta())

atualizar_lista()
janela.mainloop()
import tkinter as tk
from tkinter import ttk,messagebox

def aplicar_cupom_errado(carrinho: dict,percentual: float) -> float:
    total = sum(item["preco"] for item in carrinho["itens"])
    media = total / len(carrinho["itens"])
    return total - (total * percentual /100)

def processar_cupom():
    carrinho = obter_cupom()
    try:
        cupom = float(ent_cupom.get())
    except ValueError:
        cupom = 10.0
    try:
        resultado = aplicar_cupom_errado(carrinho, cupom)
        lbl_resultado.config(text=f"Sucesso! Total: R$ {resultado:.2f}", fg="green")
    except Exception as e:
        lbl_resultado.config(text=f"Sistema Travou!!\n {type(e).__name__}: {e}", fg="red")
        messagebox.showerror("Erro de Execucao (bug)", f"O sistema travou devido a um erro unhandled\n{type(e).__name__}: {e}")

def obter_carrinho():
    if combo_carrinho.get()== "Carrinho Vazio []":
        return {"itens": []}
    return {"itens": [
        {"nome": "Mouse", "preco": 50.0},
        {"nome": "Teclado", "preco": 150.0}]}

app = tk.Tk()
app.title("Sistema de vendas - versao com defeito")
app.geometry("400x300")
app.resizable(False, False)

tk.Label(app, text="Aplicacao de cupom (com defeito)", font=("Arial", 12, "bold"), fg="#d9534f").pack(pady=10)

tk.Label(app,text="Estado do carrinho:").pack(anchor="w", padx=20)
combo_carrinho = ttk.Combobox(app, values=["Carrinho Vazio []", "Carrinho com itens [R$ 200.00]"], state="readonly")
combo_carrinho.current(0)
combo_carrinho.pack(fill="x", padx=20, pady=5)

tk.Label(app, text="Desconto (%)").pack(anchor="w", padx=20 , pady=(10,0))

ent_cupom = tk.Entry(app)
ent_cupom.insert(0, "10")
ent_cupom.pack(fill="x", padx=20, pady=5)

tk.Button(app, text="apicar cupom", bg="red", fg="wite", font=("Arial", 10, "bold"), command=processar_cupom).pack(pady=15)
lbl_resultado = tk.Label(app, text="", font=("Arial", 10, "bold"), wraplength=360)
lbl_resultado.pack(pady=10)

app.mainloop()
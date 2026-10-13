caminho = "veiculos_gerais.txt"; frota = []
class Veiculo:
    def __init__(self, nome, cor, ano):self.nome = nome; self.cor = cor; self.ano = ano
    def acelerar(self): print(self.nome, "está acelerando")
    def frear(self): print(self.nome, "está freiando")
    def esquerda(self): print(self.nome, "virou para esquerda")
    def direita(self): print(self.nome, "virou para direita")
class Carro(Veiculo):pass
class Moto(Veiculo):pass
class Caminhao(Veiculo):pass
def carregar_frota():
    try:
        with open(caminho, 'r') as arquivo:
            for linha in arquivo:
                if linha.strip() == "":continue;tipo, resto = linha.strip().split(" = ");nome, cor, ano = resto.split(" - ")
                if tipo == "carro":frota.append(Carro(nome, cor, ano))
                elif tipo == "moto":frota.append(Moto(nome, cor, ano))
                elif tipo == "caminhao":frota.append(Caminhao(nome, cor, ano))
    except FileNotFoundError:pass;carregar_frota()
while True:
    acao = input("Deseja sair ou apagar a frota? (sair/apagar/continuar): ")
    if acao == "sair":break
    elif acao == "apagar":
        frota.clear()
        with open(caminho, 'w') as arquivo:arquivo.write('')
        print("Frota apagada!");continue
    elif acao != "continuar":print("Opção inválida!");continue
    pergunta = input("Qual veículo quer usar? (carro/moto/caminhao): ")
    if pergunta not in ["carro", "moto", "caminhao"]:print("Opção inválida!");continue
    add = input("Deseja adicionar? (sim/nao): ")
    if add == "sim":nome = input("Nome: ");cor = input("Cor: ");ano = input("Ano: ")
    if pergunta == "carro":v = Carro(nome, cor, ano)
    elif pergunta == "moto":v = Moto(nome, cor, ano)
    elif pergunta == "caminhao":v = Caminhao(nome, cor, ano);frota.append(v);print("Veículo adicionado!")
    with open(caminho, 'a') as arquivo:arquivo.write(pergunta + " = " + nome + " - " + cor + " - " + ano + "\n");dirigir = input("Deseja dirigir? (sim/nao): ")
    if dirigir == "sim":nome = input("Qual nome do veículo? ");encontrado = False
    for v in frota:
        if v.nome == nome:encontrado = True;print("Você está usando", v.nome)
        while True:acao = input("acelerar / frear / esquerda / direita / estacionar: ")
    if acao == "acelerar":v.acelerar()
    elif acao == "frear":v.frear()
    elif acao == "esquerda":v.esquerda()
    elif acao == "direita":v.direita()
    if not encontrado:print("Veículo não encontrado!")
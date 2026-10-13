class eletronico:
    def __init__(self,nome):
        self.nome = nome
        self.ligado = False

    def ligar(self):
        if not self.ligado:
            self.ligado = True
            print(f'{self.nome} esta ligado')

    def desligar(self):
        if self.ligado:
            self.ligado = False
            print(f'{self.nome} esta ligado') 

    def hibernar(self):
        print(f'{self.nome} hibernou')           
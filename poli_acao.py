class som:
    def __init__(self, nome):
        self.nome = nome
        

    def aumentar_volume(self):
            print(f'{self.nome} aumentou o volume')

    def diminuir_volume(self):
        print(f'{self.nome} diminuiu o volume')    

class rede:
    def __init__(self, nome):
        self.nome = nome

    def conectar_na_rede(self):
        print(f'{self.nome} conectou na rede')

    def desconectar_da_rede(self):
        print(f'{self.nome} desconectou da rede')

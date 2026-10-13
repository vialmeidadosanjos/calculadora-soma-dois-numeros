from abc import ABC, abstractmethod

class personagem(ABC):
    def __init__(self, mensagem):
        self.mensagem = mensagem

    @abstractmethod
    def movimentar(self):
        ...

class Movimento_esquerda(personagem):
    def movimentar(self):
        if movimentos == 'a':
            print(self.mensagem)
            return True
        return False
           
class Movimento_direita(personagem):
    def movimentar(self):
        if movimentos == 'd':
            print(self.mensagem)
            return True
        return False
    
class Movimento_ir_pra_frente(personagem):
    def movimentar(self):
        if movimentos == 'w':
            print(self.mensagem)
            return True
        return False

class Movimento_ir_pra_tras(personagem):
    def movimentar(self):
        if movimentos == 's':
            print(self.mensagem)
            return True
        return False
              
def mover(parametro: personagem):
    acao = parametro.movimentar()
    if acao == True:
        print('sim')
    else:
        print('Parado')

while True:
    movimentos = input('digite um das opções: w, a, s, d ou sair ')
    
    if movimentos == 'a':
        movimentar_pra_esquerda = Movimento_esquerda('O personagem está se movimentado pra esquerda')
        mover(movimentar_pra_esquerda)
    if movimentos == 'd':
        movimentar_pra_direita = Movimento_direita('O personagem está se movimentado pra direita')
        mover(movimentar_pra_direita)
    if movimentos == 'w':
        movimentar_pra_frente = Movimento_ir_pra_frente('O personagem está se movimentado pra frente')
        mover(movimentar_pra_frente)
    if movimentos == 's':
        movimentar_pra_tras = Movimento_ir_pra_tras('O personagem está se movimentado pra trás')
        mover(movimentar_pra_tras)
    if movimentos == 'sair':
        break

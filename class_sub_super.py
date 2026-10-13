class Pessoa:
    cpf = '1234'

    def __init__(self, nome, sobrenome):
        self.nome = nome
        self.sobrenome = sobrenome
    def falar_nome_classe(self):
        print('CLASSE PESSOA')
        print(self.nome, self.sobrenome, self.__class__.__name__)

class Cliente(Pessoa):
    def falar_nome_classe(self):
        print('EITA, nem sai da classe Cliente')
        print(self.nome, self.sobrenome, self.__class__.__name__)



class Aluno(Pessoa):
    ...
c1 = Cliente('Luiz', 'Otavio')
c1.falar_nome_classe()
a1 = Aluno('Marta', 'Helena')
a1.falar_nome_classe
print(a1.cpf)                 
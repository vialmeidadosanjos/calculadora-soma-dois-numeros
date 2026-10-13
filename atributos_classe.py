caminho = "C:\\Users\\Aluno\\vini\\ViniciusPhyton\\idade.txt"
caminho = "idade.txt"

class Pessoa:
    ano_atual = 2026

    def __init__(self, nome, ano, idade):
        self.nome = nome
        self.ano = ano
        self.idade = idade

    def idade(self):
        return Pessoa.ano_atual - self.ano
        
nome = input('Digite seu nome ')
ano = int(input('Digite seu ano de nascimento '))
idade = Pessoa.ano_atual - ano
p = Pessoa(nome , ano, idade)
with open(caminho, 'a') as arquivo:
        print(f'{nome},{ano},{idade}',file=arquivo)

print('Seu nome é:', p.nome)
print('Sua idade é:', p.idade())    
class Pessoa:
    def __init__(self, nome, idade,  carreiras):
        self.nome = nome
        self.idade = idade
        self.carreiras = carreiras

@classmethod
def metodo_de_classe(cls):
    print('Helo,, ola!!!')        
@classmethod
def criar_com_50_anos(cls, nome):
    return cls(nome, 50, 'manicure')
@classmethod
def criar_sem_nome(cls, idade):
    return cls('anonima', idade, 'soldador')
@classmethod
def modifica_idade(cls, idade):
    return cls('julia', idade, 'manicure')
@classmethod
def carreira(cls, carreiras):
    return cls('Marcos', 34, carreiras)


p1 = Pessoa('Joao', 34, 'soldador')
p2 = Pessoa.criar_com_50_anos('helena')        
p3 = Pessoa('anonima', 23, 'soldador')
p4 = Pessoa.modifica_idade(16)
p5 = Pessoa.carreira('pintor')

print(Pessoa.metodo_de_classe())
print (f'O {p1.nome}, tem a idade {p1.idade}, e sua profissão é: {p1.carreira}')
print (f'A {p2.nome}, tem a idade {p2.idade}, e trabalha de: {p2.carreira}')
print (p3.nome, p3.idade, p3.carreira)
print (f'A {p4.nome}, tem a idade {p1.idade}, e trabalha de: {p1.carreira}')
print (p1.nome, p1.idade, p1.carreira)
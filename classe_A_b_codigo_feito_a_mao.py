class Produto:
    def __init__(self, nome, tipo):
        self.nome = nome
        self.tipo = tipo

    def __str__(self):   #define um objeto de uma classe que deve ser representado como uma string 
        return f'Produto: {self.nome} é do tipo: {self.tipo}'
    
class produto_perecivel(Produto):
    def __init__(self, nome, tipo, perceciveis):
        super().__init__(nome, tipo)
        self.pereciveis = perceciveis

    def mostrar(self):
        if self.pereciveis:
            print(f'{self.nome} é perecivel')
        else:
            print(f'{self.nome} não é perecivel')

nome = input('Digite o nome: ')                    
tipo = input('Digite o tipo: ')                 
perecivel = input('E perececivel? (s/n) ') == 's'

produto = produto_perecivel(nome, tipo, perecivel)

print(produto)
produto.mostrar()


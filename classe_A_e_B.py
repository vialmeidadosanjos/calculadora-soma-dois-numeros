#class a:
    #def metodo(self):
        #print('A')

#class b(a):
    #def metodo(self):
        #print('b')

#class C(b):
    #def metodo(self):
        #super().metodo()
        #print('c')

#c = C()  
#print(c.atributo_a)
#print(c.atributo_b) 
#print(c.atributo_c)
#c.metodo()

#--------------------------------------------------------------------------------------
#class Produto:
    #def __init__(self, nome, tipo_produto):
        #self.nome = nome
       # return f'Produto: {self.nome} do tipo: {self.tipo_produto}'


#class ProdutoPerecivel(Produto):
    #def __init__(self, nome, tipo_produto, perecivel):
        #Produto.__init__(self, nome, tipo_produto)  
        #self.perecivel = perecivel
        #self.tipo_produto = tipo_produto

    #def mostrar(self):
        #if self.perecivel:
            #print(f'{self.nome} é perecível')
        #else:
            #print(f'{self.nome} não é perecível')
#produto1 = ProdutoPerecivel('Refrigerante','Bebida', True)
#produto2 = ProdutoPerecivel('Bicicleta','Brinquedo', False)

#print(produto1)
#print(produto2)
#produto1.mostrar()            
#produto2.mostrar()
#  
# ---------------------------------------------------------------------------

class Produto:
    def __init__(self, nome, tipo_produto):
        self.nome = nome
        self.tipo_produto = tipo_produto

    def __str__(self):
        return f'Produto: {self.nome} é do tipo: {self.tipo_produto}'


class ProdutoPerecivel(Produto):
    def __init__(self, nome, tipo_produto, perecivel):
        super().__init__(nome, tipo_produto)
        self.perecivel = perecivel

    def mostrar(self):
        if self.perecivel:
            print(f'{self.nome} é perecível')
        else:
            print(f'{self.nome} não é perecível')


while True:

    nome = input("Digite o nome do produto: ")
    tipo = input("Digite o tipo do produto: ")
    perecivel = input("Ele é perecível? (s/n): ").lower() == 's'

    produto = ProdutoPerecivel(nome, tipo, perecivel)

    print(produto)
    produto.mostrar()

    continuar = input("Deseja cadastrar outro produto? (s/n): ").lower()
    if continuar != 's':
        break
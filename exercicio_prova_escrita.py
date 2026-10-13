class empresa:
    def __init__(self, nome, razao_social, cnpj ):
        self.nome = nome
        self.razao_social = razao_social
        self.cnpj = cnpj

    def mostrar(self):
        print(f'A {self.nome}, tem como razao social {self.razao_social}, seu CNPJ\
        {self.cnpj}')

class endereco(empresa):
    def __init__(self, rua, numero, bairro, cidade, cep, nome, razao_social, cnpj): 
        super().__init__(nome, razao_social, cnpj)
        self.rua = rua
        self.numero = numero
        self.bairro = bairro
        self.cidade = cidade                                                                                
        self.cep = cep

    def mostrar(self):
        super().mostrar()
        print(f'Situada na rua {self.rua},{self.numero} e bairro {self.bairro}, na\
        cidade de {self.cidade}, com CEP {self.cep}')

class ramo_de_atuacao(endereco):
    def __init__(self, tipo, observacao, rua, numero, bairro, cidade, cep, nome, razao_social, cnpj):
        super().__init__(rua, numero, bairro, cidade, cep, nome, razao_social, cnpj)
        self.tipo = tipo
        self.observacao = observacao

    def mostrar(self):
        super().mostrar()
        print(f'Atua no ramo de tipo {self.tipo}, tendo como observação {self.observacao}')    

nome1 = input('digite o nome fantasia: ')
razao1 = input('digite a razão social: ')
cnpj1 = int(input('digite o cnpj: '))
rua1 = input('digite a rua: ')
numero1 = int(input('digite o número da empresa: '))
bairro1 = input('digite o bairro: ')
cidade1 = input('digite a cidade: ')
cep1 = input('digite o cep: ')
tipo1 = input('digite o tipo da empresa: ')
observacao1 = input('digite a observação da empresa: ')

empresa1 = ramo_de_atuacao(tipo1, observacao1, rua1, numero1, bairro1, cidade1, cep1, nome1, razao1, cnpj1)
empresa1.mostrar()
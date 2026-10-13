class carro:
    def __init__(self, nome, marca, cor):
        self.nome = nome
        self.cor = cor
        self.marca = marca


veiculo1 = carro('fiesta', 'ford', ' preto') 
veiculo2 = carro('fusca', 'Wolkswagen', 'Azul')
veiculo3 = carro('uno', 'fiat', 'vermelho') 
veiculo4 =carro('corolla', 'toyota', 'amarelo') 
veiculo5 = carro('polo', 'Wolkswagem', 'cinza')


def acelerar(self):
        print(f"{self.nome} está acelerando")   
def frear(self):
        print(self.nome, 'está freando')

print('veiculo1',veiculo1.nome,veiculo1.marca,veiculo1.cor)
print('veiculo2',veiculo2.nome,veiculo2.marca,veiculo2.cor)
print('veiculo3',veiculo3.nome,veiculo3.marca,veiculo3.cor)
print('veiculo4',veiculo4.nome,veiculo4.marca,veiculo4.cor)
print('veiculo5',veiculo5.nome,veiculo5.marca,veiculo5.cor)

escolha = int(input('Digite um numero de 1 á 5: '))
if escolha == 1:
    print(f'Voce escolheu o fiesta')
if escolha == 2:
    print(f'Voce escolheu o carro: fusca Wolkswagen Azul')
if escolha == 3:
    print(f'Voce escolheu o carro: uno fiat vermelho')
if escolha == 4:
    print(f'Voce escolheu o carro: corolla toyota amarelo')
if escolha == 5:
    print(f'Voce escolheu o carro: polo Wolkswagem cinza')


while True:
     acao = input('Vc deseja sair, acelerar ou freiar? ') 

     if escolha == 1:
          if acao == 'acelerar':
               print('fiesta está acelerando')
          if acao == 'freiar':
               print('fiesta freiou')
          if acao == 'sair':
               print('programa encerrado')
               break 
     if escolha == 2:
          if acao == 'acelerar':
               print('fusca está acelerando')
          if acao == 'freiar':
               print('fusca freiou')
          if acao == 'sair':
               print('programa encerrado')
               break 

     if escolha == 3:
          if acao == 'acelerar':
               print('uno está acelerando')
          if acao == 'freiar':
               print('uno freiou')
          if acao == 'sair':
               print('programa encerrado')
               break 
     if escolha == 4:
          if acao == 'acelerar':
               print('corolla está acelerando')
          if acao == 'freiar':
               print('corolla freiou')
          if acao == 'sair':
               print('programa encerrado')
               break 
     if escolha == 5:
          if acao == 'acelerar':
               print('polo está acelerando')
          if acao == 'freiar':
               print('polo freiou')
          if acao == 'sair':
               print('programa encerrado')
               break                                                                            
caminho = "C:\\Users\\Aluno\\vini\\ViniciusPhyton\\carro.txt"
caminho = "carro.txt"


class carro:
    def __init__(self, nome):
        self.nome = nome
        
    def acelerar(self):
        print(f"{self.nome} está acelerando")   
    def frear(self):
        print(f"self.nome, está freando")
frota = []
while True:
    escolha = input('Voce deseja adicionar ou dirigir um carro? ')
    if escolha == 'adicionar':
        nome = input('Informe o nome do carro: ')
        with open(caminho, 'a') as arquivo:
            print(nome,file=arquivo)
        veiculo = carro(nome)
        frota.append(veiculo)
        print(f'O carro {nome} foi adicionado a frota ')     

    elif escolha == 'dirigir':
        while True:
            escolher = input(' Digite o nome do carro ')
            car =  None
            for c in frota: # serve para escolher o carro
                if c.nome == escolher:  # serve para escolher o carro
                    car = c
            if car:
                comando = input('Vc quer acelerar, freiar ou sair? ')
                if comando == 'acelerar':
                    car.acelerar()
                elif comando == 'freiar':
                    car.freiar()
                elif comando == 'sair':
                    print('O programa foi encerrado ')    
                break
            else:
                print('Comando invalido')
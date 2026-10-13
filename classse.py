class carro:
    def __init__(self, nome, marca, cor):
        self.nome = nome
        self.cor = cor
        self.marca = marca

    def acelerar(self):
        print(f"{self.nome} está acelerando")   
    def frear(self):
        print(self.nome, 'está freando')    
veiculo1 = carro('fiesta', 'ford', ' preto') 
veiculo2 = carro('fusca', 'Wolkswagen', 'Azul')
veiculo3 = carro('uno', 'fiat', 'vermelho') 

print(veiculo1.nome,veiculo1.marca,veiculo1.cor)
print(veiculo2.nome,veiculo2.marca,veiculo2.cor)
print(veiculo3.nome,veiculo3.marca,veiculo3.cor)
veiculo2.acelerar()
veiculo2.frear()


#vcs criar um programa onde o usuario vai escolher entr 5 carros
# e vai dar o comando de acelerar ou frear
#mostre as ações
# e tmb vai ter o comando de sair do comando se quiser a qulquer momento.
# estrutur de seleçao para tomara decisao
class fabricante:
    def __init__(self, nome):
        self.nome = nome

class motor:
    def __init__(self, potencia):
        self.potencia = potencia

class carro:
    def __init__(self, modelo):
        self.modelo = modelo
        self.fabricante =  None
        self.motor = None



    @property
    def motor(self):
        return self._motor
    
    @motor.setter
    def motor(self,valor):
       self._motor = valor

    @property
    def fabricante(self):
        return self._fabricante
    
    @fabricante.setter
    def fabricante(self,valor):
       self._fabricante = valor
veiculo1 = carro(input("Digite o nome do veiculo: "))
motor1 = motor(input("Digite o motor do veiculo: "))
fabricante1 = fabricante(input("Digite o fabricante do veiculo: "))

veiculo1.motor = motor1
veiculo1.fabricante = fabricante1

print(f"o carro {veiculo1.modelo}, tem o motor {veiculo1.motor.potencia} e foi fabricado pela {veiculo1.fabricante.nome}")




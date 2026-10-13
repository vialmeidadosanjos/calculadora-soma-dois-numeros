from poli_eletronico import eletronico
import poli_acao

class computador(eletronico,poli_acao.som,poli_acao.rede):
    def ligar(self):
        super().ligar()
    def desligar(self):
        super().desligar()
    def aumentar_volume(self):
        super().aumentar_volume()
    def diminuir_volume(self):
        super().diminuir_volume() 
    def conectar_na_rede(self):
        super().conectar_na_rede()
    def desconectar_da_rede(self):
        super().desconectar_da_rede()
    def hibernar(self):
        super().hibernar()    

class teve(eletronico,poli_acao.som,poli_acao.rede):
    def ligar(self):
        super().ligar()
    def desligar(self):
        super().desligar()
    def aumentar_volume(self):
        super().aumentar_volume()
    def diminuir_volume(self):
        super().diminuir_volume() 
    def conectar_na_rede(self):
        super().conectar_na_rede()
    def desconectar_da_rede(self):
        super().desconectar_da_rede() 

class som(eletronico,poli_acao.som):
    def ligar(self):
        super().ligar()
    def desligar(self):
        super().desligar()
    def aumentar_volume(self):
        super().aumentar_volume()
    def diminuir_volume(self):
        super().diminuir_volume()  
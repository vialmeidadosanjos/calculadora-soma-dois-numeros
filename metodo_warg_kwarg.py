class carro:
    @staticmethod
    def funcao_que_esta_na_classe(*arg,**kwargs):
        print('ola', arg , kwargs)

def funcao(*arg,**kwargs):
    print('oi',arg,kwargs)

class moto:
    @staticmethod
    def funcao_que_esta_na_classe(**kwargs):
        print('oi', kwargs)

    def funcao(*arg,**kwargs):
        print('oi', arg,kwargs)

c1 = carro()
c1 = moto()
c1.funcao_que_esta_na_classe(a='banana',f='passego',e='morango')
funcao(1,2,3,4,5,6,7,234,68,'34t6')
print()
carro.funcao_que_esta_na_classe()
moto.funcao_que_esta_na_classe()
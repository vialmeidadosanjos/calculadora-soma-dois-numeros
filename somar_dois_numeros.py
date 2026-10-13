
soma = 0

while True:
    numero = input('Digite um numero para somar ') 
    if numero == 'sair':
        print('programa encerrado')
        break
    if numero.isdigit():
        soma+= int(numero)
        print(' a soma é : ', soma)

    else:
        print('A entrada foi invalida, por favor digite "sair" ou um numero ')

    


peso = float(input('digite seu peso em kg '))
altura = float(input('digite sua altura '))

imc = peso/ (altura**2)
print(f'seu imc é: {imc:.2f}')
 
if imc < 18.5:
    print(' voce esta abaixo do peso')

elif 18.5  and imc < 24.9:
    print(' voce esta com peso normal')

elif 25  and imc < 29.9:
    print('voce esta com sobrepeso')

elif 30  and imc < 34.9:
    print('voce esta com obesidade grau 1 ')

elif 35 and imc < 39.9:
    print('voce esta com obesidade grau 2 ') 

else:
     print('voce esta com obesidade grau 3 Morbida')  
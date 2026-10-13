num1 = float(input('Digite o primeiro numero '))
num2 = float(input('Digite o segundo numero '))
soma = num1 + num2
print(f' o resultado é: {soma}')

while True:
    opcao = input(' se vc deseja somar mais um numero digite "sim", se nao desja digite "não"')
    if opcao == 'não':
        print('Programa encerrado')
        break
    elif opcao == 'sim':
        try:
            num1 = (input('Digite mais um numero '))
            soma += float(num1)

            print(f'O resultado agora é: {soma}')
        except ValueError:
            print(' isso não é um numero valido')
    else:
        print('opção invalida')            
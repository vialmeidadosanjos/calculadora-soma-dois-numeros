import math

a=float(input('escreva o valor de a: '))
b=float(input('escreva o valor de b: '))
c=float(input('escreva o valor de c: '))

delta = float(b**2) - 4 * a *c

x1 =(-b + math.sqrt(delta)) /2*a

x2 =(-b - math.sqrt(delta)) /2*a

print('o valor do x1 é: ', x1)
print('o valor do x2 é: ', x2)
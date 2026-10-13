nome = input('digite seu nome ')
print(nome[::1]) #pra escrever o nome digitado na ordem normal

print()

print(nome[::-1]) # pra escrever o nome invertido

print()

quantidade_de_letras = len(nome)
print('O nome tem', quantidade_de_letras, 'letras')

print()

print('A primeira letra do nome digitado é ', nome[0]) #pra aparecer a primeira lettra do nome digitado

print()

print('A ultima letra do nome digitado é ',nome[-1]) #pra escrever a ultima lettra do nome digitado

print()

espaco_vazio =int(nome.count(" "))
print('existe', espaco_vazio, 'espaços vazios nesse nome')



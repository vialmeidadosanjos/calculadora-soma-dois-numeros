usuario = 'Admin'
senha = 'Admin123'

nome_usuario = input('Digite o nome do usuario ')
senha_usuario = input('Digite a senha ')

if usuario == nome_usuario and senha == senha_usuario:
    print('o usuario e a senha estao corretos') 

elif usuario != nome_usuario and senha !=  senha_usuario:
    print('o usuario e a senha estao incorretos') 
      
elif usuario == nome_usuario and senha !=  senha_usuario:
    print('o usuario esta correto e a senha está incorreta')

if usuario != nome_usuario and senha ==  senha_usuario:
    print('o usuario esta incorreto e a senha está correta')

if nome_usuario == '' and senha == senha_usuario:
    print('digite o nome de usuario')

if nome_usuario == nome_usuario and senha_usuario == '':
    print('digite a senha do usuario')

if nome_usuario == '' and senha_usuario == '':
    print('digite o nome de usuario')
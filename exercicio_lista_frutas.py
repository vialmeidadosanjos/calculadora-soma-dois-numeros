frutas = ['Maçã',#posiçao 0
          'Banana',#posiçao 1
          ' Pera',#posiçao 2
          'caju',#posiçao 3
          'Caja', #posiçao 4
          'Morango',#posiçao 5
          'graviola',#posiçao 6
          'melancia',#posiçao 7
          'melao',#posiçao 8
          'manga',#posiçao 9
          'maracuja',#posiçao 10
          'uva',#posiçao 11
          'goiaba',#posiçao 12
          'kiwi',#posiçao 13
          'amora',#posiçao 14
          'ameixa',#posiçao 15
          'coco',#posiçao 16
          'jabuticaba',#posiçao 17
          'lichia',#posiçao 18
          'pessego',]#posiçao 19
#-------------------------------------------------------------------------------------------
print(frutas)
posicao_fruta = int(input(' digite um numero de 0 á 19 e de acordo com esse numero vai aparecer uma fruta '))
if posicao_fruta < len(frutas):
    print(f"A Fruta correspondente na posição, {posicao_fruta}, é {frutas[posicao_fruta]}")
#--------------------------------------------------------------------------------------------


nova_fruta = input(' digite uma nova fruta que vc deseja ')
frutas.append(nova_fruta)
#--------------------------------------------------------------------------------------------
deletar_fruta = int(input('digite a fruta que vc deseja deletar '))
del frutas[deletar_fruta]

print('Lista das frutas atualizadas ')
print(frutas)

for i in frutas:
    print(i)
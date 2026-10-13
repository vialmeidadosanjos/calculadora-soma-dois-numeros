import os

caminho = "C:\\Users\\Aluno\\vini\\ViniciusPhyton\\aula.txt"
caminho = "aula.txt"


while True:
    escolha = input(' voce deseja adicionar, listar ou excluir algo? ')

    if escolha == "adicionar":
        lista_de_tarefas = input('Digite uma tarefa: ')
        with open(caminho, 'a') as arquivo:
            print(lista_de_tarefas,file=arquivo)

    elif escolha == "listar":
        with open(caminho, 'r') as arquivo:
            print(arquivo.read())

    elif escolha == "excluir":
        os.unlink(caminho)


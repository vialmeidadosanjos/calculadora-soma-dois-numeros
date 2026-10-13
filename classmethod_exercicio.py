class aluno:
    nomes = []
    def __init__(self, nome):
        self.nome =  nome

    
while True:
    nome_alunos = input('Digite um nome ou digite "sair" para sair do programa ')
    if nome_alunos == 'sair':
        print(f'A quantidade de nomes digitados é: {len(aluno.nomes)}')
        break

    else:
        aluno.nomes.append(nome_alunos) 
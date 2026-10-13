# primeira forma de fazer
#class Pessoa:
 #   total_alunos = 0
#    def __init__(self, nome):
#        self.nome = nome
#        Pessoa.total_alunos += 1
#    @classmethod
#    def exibir_resultado(cls):
#        print(f'O total de alunos agrora é: {cls.total_alunos}')


#p1 = pessoa('beto')
#p2 = pessoa('maria')
#p3 = pessoa('') 

#-------------------------------------------------------------------------------------            
#segunda forma de fazer

class aluno:
     total_aluno = 0
     def __init__(self,nome):
         self.nome = nome
         aluno.total_aluno += 1
     @classmethod
     def exibir_resultado(cls):
         print(f"O total de alunos agora é {cls.total_aluno}")
while True:
     nome = input('Digite o nome do aluno ou digite "sair" pra encerrar: ')
     if nome.lower() == 'sair':
         aluno.exibir_resultado()
         break
     novo_aluno = aluno(nome)
     aluno.exibir_resultado()
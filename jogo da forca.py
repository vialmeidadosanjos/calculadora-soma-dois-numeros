import random
def escolher_palavra():
    palavras = ["neymar", "messi", "ronaldo", "mbappe", "lewandowski", "salah", "kane", "haaland"]
    return random.choice(palavras)       #Escolhe uma palavra aleatória da lista para o jogo da forca
def jogar():
    palavra = escolher_palavra()
    letras_descobertas = set()     #Conjunto para armazenar as letras que o jogador já descobriu
    tentativas = 6
    while tentativas > 0:
        for letra in palavra:
            if letra in letras_descobertas:    #Verifica se a letra já foi descoberta e a exibe, caso contrário exibe um "_"
                print(letra, end=" ")
            else:
                print("_", end=" ")
        print()
        chute = input("Digite uma letra: ").lower()   #Solicita ao jogador que digite uma letra e converte para minúscula
        if chute in palavra:
            letras_descobertas.add(chute)
            if all(letra in letras_descobertas for letra in palavra):   #Verifica se todas as letras da palavra foram descobertas
                print(f"Parabéns! Você descobriu a palavra: {palavra}")  
                return
        else:
            tentativas -= 1
            print(f"Letra incorreta! Tentativas restantes: {tentativas}")  
    print(f"Game Over! A palavra era: {palavra}")
if __name__ == "__main__":
    jogar()
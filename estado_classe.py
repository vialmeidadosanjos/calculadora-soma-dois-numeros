class camera:
    def __init__(self, nome, filmando = False, fotografar = False):
       self.nome = nome
       self.filmando = filmando
       self.fotografar = fotografar

    def filmar(self):
        if self.filmando:
            print(f"{self.nome} já está filmando")
            return
        print(f'{self.nome} está filmando')
        self.filmando = True
    def foto(self):
        print(f"{self.nome} esta tirando uma foto")
        self.filmando = True

c1 = camera('sony')
c2 = camera('nikon')
c3 = camera('canon') 
print(c1.filmando)
c1.filmar()
print(c1.filmando)
c1.filmar()


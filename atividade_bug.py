preco = float(input("Digite o valor do produto: "))
desconto = float(input(" digite o valor do desconto: "))

def calcular_tudo():
    resultado = preco* (desconto /100)
    resultado_completo = preco - resultado
    print(resultado_completo)

calcular_tudo()

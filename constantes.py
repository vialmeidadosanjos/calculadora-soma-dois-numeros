# constantes sao valores que nunca vao mudar

#DECLARAÇÃO DE VARIAVEIS
velocidade = 61
local_radar = 101

#ESSAS ABAIXO SAO DECLARAÇAO DE CONSTANTES
RADAR_1 = 60
LOCAL_1 = 100
RADAR_RANGE = 1

if velocidade > RADAR_1:
    print('velocidade do carro passou do radar 1 ')
if local_radar >= (LOCAL_1 - RADAR_RANGE) and local_radar <= (LOCAL_1 + RADAR_RANGE) and velocidade >RADAR_1:
    print(' o carro foi multado')
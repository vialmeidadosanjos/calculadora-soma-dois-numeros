from abc import ABC, abstractmethod
class Notificacao(ABC): #04 testando e-mail
    def __init__(self, mensagem):
        self.mensagem = mensagem

    @abstractmethod
    def enviar(self) -> bool:
        ...
class NotificacaoEmail(Notificacao): #02
    def enviar(self) -> bool:
        print(f'E-mail: enviando - {self.mensagem}')
        return True
    
class NotificacaoSmS(Notificacao): #02
    def enviar(self) -> bool:
        print(f'Sms: enviando - {self.mensagem}')
        return True    

def notificar(parametro: Notificacao):
    notificacao_enviada = parametro.enviar()
    if notificacao_enviada:
        print('Notificação enviada')
    else:
        print('Notificação Não enviada')
notificacao_email = NotificacaoEmail('testando e-mail')
notificar(notificacao_email)            
notificacao_sms = NotificacaoSmS('testando SmS')
notificar(notificacao_sms)
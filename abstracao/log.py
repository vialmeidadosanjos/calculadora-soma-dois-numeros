class Log:
    def _log(self, msg):
        raise NotImplementedError('Implemente o metodo log')
    
    def log_error(self, msg):
        return self._log(f'Erro: {msg}')
    
    def log_success(self, msg):
        return self._log (f'Success: {msg}')
        
class LogFileMixin(Log):
    def _log(self, msg):
        print(msg)


class LogPrintMaxin(Log):
    def _log(self, msg):
        print(f'{msg} ({self.__class__.__name__})')

if __name__ == '__main__':
    l = LogPrintMaxin()
    l.log_error('Qualquer coisa') 
    l.log_success('Sucesso')
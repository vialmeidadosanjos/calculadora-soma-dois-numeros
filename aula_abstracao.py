# from abc import ABC, abstractmethod

# class AbstractFoo(ABC):
#     def __init__(self, name):
#         self.name = name

#     @property
#     def name (self):
#         return print('Agora eu estou aqui:')

#     @name.setter
#     def name(self, name):
#         print('Estou antes de:')

# class Foo(AbstractFoo):
#     def __init__(self, name):
#         super().__init__(name)
#         print('Continuo inutil')
        
# foo = Foo('Bar')
# print(foo.name) 

from abc import ABC, abstractmethod

class AbstractFoo(ABC):
    def __init__(self, name):
        self.name = name
        self._name = name
        
    @property
    def name (self):
         print('Agora eu estou aqui:')
         return f'{self._name}'
    
    @name.setter
    def name(self, name):
        print('Estou antes de:')

class Foo(AbstractFoo):
    def __init__(self, name):
        super().__init__(name)
        print('Continuo inutil')

foo = Foo('Bar')
print(foo.name)                               
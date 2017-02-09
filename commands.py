import re
import string
import inspect


__all__ = [
    'MetroStatusCommand',
    'TramStatusCommand'
]


class Command:
    names = []
    
    def get_names(self):
        if not self.names:
            raise ValueError('self.names must contain at least one name')
        
        return self.names
    
    def get_params(self):
        return inspect.signature(self.run).parameters.keys()
    
    def run(self):
        raise NotImplementedError('Must be implemented')


class MetroStatusCommand(Command):
    names = ['métro', 'metro']
    
    def run(self, line):
        return 'OK'


class TramStatusCommand(Command):
    names = ['tram']
    
    def run(self, line):
        return 'OK'

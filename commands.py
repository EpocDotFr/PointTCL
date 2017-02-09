import inspect


__all__ = [
    'HelpCommand',
    'MetroStatusCommand',
    'TramStatusCommand',
    'BusStatusCommand',
    'FunicularStatusCommand'
]


class Command:
    names = []
    slack_client = None

    user = None
    channel = None
    
    def get_names(self):
        if not self.names:
            raise ValueError('self.names must contain at least one name')
        
        return self.names
    
    def get_params(self):
        return inspect.signature(self.run).parameters.keys()

    def run(self):
        raise NotImplementedError('Must be implemented')


class HelpCommand(Command):
    names = ['aide', 'help']
    
    def run(self):
        return 'OK'


class MetroStatusCommand(Command):
    names = ['métro', 'metro']

    def run(self, line):
        return 'OK'


class TramStatusCommand(Command):
    names = ['tram']
    
    def run(self, line):
        return 'OK'


class BusStatusCommand(Command):
    names = ['bus']

    def run(self, line):
        return 'OK'


class FunicularStatusCommand(Command):
    names = ['funiculaire', 'funi']

    def run(self, line):
        return 'OK'

from models import *
import inspect


__all__ = [
    'HelpCommand',
    'SubwayStatusCommand',
    'TramStatusCommand',
    'BusStatusCommand',
    'FunicularStatusCommand'
]


class Command:
    names = []
    bot = None

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
    names = ['aide', 'help', 'comment', 'dafuq', 'wut']

    def run(self):
        help_answer = """
Déjà : bonjour.

Comment ça marche : en me mentionnant, le premier mot désigne sur quelle type de ligne vous souhaitez avoir des infos. Le deuxième le nom de la ligne.

Exemples :

> @pointtcl métro d
> @pointtcl tram t4
> @pointtcl bus 31 bordel
> @pointtcl funi f2

En retour je vous dit s'il y a des merdes ou pas. Rien de compliqué.
"""

        self.bot.say(help_answer, self.channel)


class SubwayStatusCommand(Command):
    names = ['métro', 'metro']

    def run(self, line):
        line_object = TclLine.query.get_for_home(TclLineType.SUBWAY, line)

        if not line_object:
            self.bot.say_random('unknown_subway_line', self.channel, user=self.user, line=line)



class TramStatusCommand(Command):
    names = ['tram']

    def run(self, line):
        pass


class BusStatusCommand(Command):
    names = ['bus']

    def run(self, line):
        pass


class FunicularStatusCommand(Command):
    names = ['funiculaire', 'funi']

    def run(self, line):
        pass

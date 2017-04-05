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


class LineCommand(Command):
    def _check(self, type, line, unknown, disrupted, ok):
        line_object = TclLine.find_line_by_type(type, line.lower())

        if not line_object:
            self.bot.say_random(unknown, self.channel, user=self.user, line=line.upper())
            return

        if line_object.is_disrupted:
            self.bot.say_random(disrupted, self.channel, line=line.upper(), since=line_object.latest_disruption_started_at.humanize(locale='FR'), reason='\n _' + line_object.latest_disruption_reason + '_' if line_object.latest_disruption_reason else '')
        else:
            self.bot.say_random(ok, self.channel, line=line.upper())


class HelpCommand(Command):
    names = ['aide', 'help', 'comment', 'dafuq', 'wut', 'hein']

    def run(self):
        help_answer = """
Déjà : bonjour.

Comment ça marche : en me mentionnant, le premier mot désigne sur quelle type de ligne vous souhaitez avoir des infos. Le deuxième le nom de la ligne.

Exemples :

> @pointtcl métro d
> @pointtcl tram t4
> @pointtcl bus 31 bordel
> @pointtcl funi f2

En retour je vous dit s'il y a un soucis ou pas.

Bien à vous,
"""

        self.bot.say(help_answer, self.channel)


class SubwayStatusCommand(LineCommand):
    names = ['métro', 'metro']

    def run(self, line):
        self._check(TclLineType.SUBWAY, line, 'unknown_subway_line', 'subway_line_disrupted', 'subway_line_ok')


class TramStatusCommand(LineCommand):
    names = ['tram']

    def run(self, line):
        self._check(TclLineType.TRAM, line, 'unknown_tram_line', 'tram_line_disrupted', 'tram_line_ok')


class BusStatusCommand(LineCommand):
    names = ['bus']

    def run(self, line):
        self._check(TclLineType.BUS, line, 'unknown_bus_line', 'bus_line_disrupted', 'bus_line_ok')


class FunicularStatusCommand(LineCommand):
    names = ['funiculaire', 'funi']

    def run(self, line):
        self._check(TclLineType.FUNICULAR, line, 'unknown_funicular_line', 'funicular_line_disrupted', 'funicular_line_ok')

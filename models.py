from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
import sqlalchemy


__all__ = [
    'TclLineType',
    'TclLine'
]


Model = declarative_base()

class TclLineType(Enum):
    SUBWAY = 'SUBWAY'
    TRAM = 'TRAM'
    BUS = 'BUS'
    FUNICULAR = 'FUNICULAR'


class TclLine(Model):
    __tablename__ = 'tcl_lines'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    type = sqlalchemy.Column(sqlalchemy.Enum(TclLineType), nullable=False)
    is_disturbed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    disturbtion_reason = sqlalchemy.Column(sqlalchemy.Text, default='')

    def __init__(self, name=None, type=None, is_disturbed=False, disturbtion_reason=''):
        self.name = name
        self.type = type
        self.is_disturbed = is_disturbed
        self.disturbtion_reason = disturbtion_reason

    def __repr__(self):
        return '<TclLine> #{} : {}'.format(self.id, self.name)

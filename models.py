from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import JSONType
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
    is_disrupted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    disruption_reasons = sqlalchemy.Column(JSONType, default=[])

    def __init__(self, name=None, type=None, is_disrupted=False, disruption_reason=[]):
        self.name = name
        self.type = type
        self.is_disrupted = is_disrupted
        self.disruption_reason = disruption_reason

    def __repr__(self):
        return '<TclLine> #{} : {}'.format(self.id, self.name)

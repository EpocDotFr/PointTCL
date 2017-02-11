from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import JSONType, ArrowType
from enum import Enum
from sqlalchemy.orm import Query
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


class TclLineQuery(Query):
    def get_for_home(self, type, name):
        q = self.filter(TclLine.type == type)
        q = q.filter(TclLine.name == name)

        return q.first()


class TclLine(Model):

    __tablename__ = 'tcl_lines'
    query_class = TclLineQuery

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    type = sqlalchemy.Column(sqlalchemy.Enum(TclLineType), nullable=False)
    is_disrupted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    disrupted_since = sqlalchemy.Column(ArrowType, default=None)
    disruption_reasons = sqlalchemy.Column(JSONType, default=[])

    def __init__(self, name=None, type=None, is_disrupted=False, disrupted_since=None, disruption_reasons=[]):
        self.name = name
        self.type = type
        self.is_disrupted = is_disrupted
        self.disrupted_since = disrupted_since
        self.disruption_reasons = disruption_reasons

    def __repr__(self):
        return '<TclLine> #{} : {}'.format(self.id, self.name)

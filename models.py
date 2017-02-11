from database import Base, db_session
from sqlalchemy_utils import JSONType, ArrowType
from enum import Enum
import sqlalchemy


__all__ = [
    'TclLineType',
    'TclLine'
]


class TclLineType(Enum):
    SUBWAY = 'SUBWAY'
    TRAM = 'TRAM'
    BUS = 'BUS'
    FUNICULAR = 'FUNICULAR'


class TclLine(Base):
    __tablename__ = 'tcl_lines'

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

    @staticmethod
    def find_line(type, name):
        q = db_session.query(TclLine).filter(TclLine.type == type)
        q = q.filter(TclLine.name == name)

        return q.first()

    def __repr__(self):
        return '<TclLine> #{} : {}'.format(self.id, self.name)

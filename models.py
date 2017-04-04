from database import Base, db_session
from sqlalchemy_utils import ArrowType
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

    def __init__(self, name=None, type=None, is_disrupted=False, disrupted_since=None):
        self.name = name
        self.type = type
        self.is_disrupted = is_disrupted
        self.disrupted_since = disrupted_since

    @staticmethod
    def find_line_by_type(type, name):
        q = db_session.query(TclLine).filter(TclLine.type == type)
        q = q.filter(TclLine.name == name)

        return q.first()

    @staticmethod
    def find_line(name):
        q = db_session.query(TclLine).filter(TclLine.name == name)

        return q.first()

    @staticmethod
    def get_disturbed_line_ids():
        q = db_session.query(TclLine).filter(TclLine.is_disrupted == True)

        lines = q.all()

        return [line.name for line in lines]

    def __repr__(self):
        return '<TclLine> #{} : {}'.format(self.id, self.name)

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
    latest_disruption_started_at = sqlalchemy.Column(ArrowType, default=None)
    latest_disruption_reason = sqlalchemy.Column(sqlalchemy.Text, default=None)

    def __init__(self, name=None, type=None, is_disrupted=False, latest_disruption_started_at=None, latest_disruption_reason=None):
        self.name = name
        self.type = type
        self.is_disrupted = is_disrupted
        self.latest_disruption_started_at = latest_disruption_started_at
        self.latest_disruption_reason = latest_disruption_reason

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

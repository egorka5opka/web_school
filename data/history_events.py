import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class HistoryEvent(SqlAlchemyBase, SerializerMixin):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    year = sqlalchemy.Column(sqlalchemy.Integer, index=True, nullable=False)
    event = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user = orm.relation('User')

    def __init__(self, year: int, event: str = "", text: str = ""):
        self.event = event
        self.year = year
        self.description = text

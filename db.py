import datetime
from typing import Optional

from flask_sqlalchemy import Model
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String

_DB: Optional[SQLAlchemy] = None


def init_db(app):
    global _DB
    if not _DB:
        _DB = SQLAlchemy(app)
    return _DB


class Statistic(Model):
    __tablename__ = "Statistics"

    # server_addr = Column(String(15))
    date = Column(DateTime)
    stats = Column(String)

    def __init__(self, date: datetime.datetime, stats: str):
        self.date = date
        self.stats = stats

    def __repr__(self):
        return f"<Statistic: {self.date}: {self.stats}>"

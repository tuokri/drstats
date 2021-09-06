import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy import String

from app import app

database = SQLAlchemy(app)


class Statistic(database.Model):
    __tablename__ = "Statistics"

    # server_addr = Column(String(15))
    date = database.Column(DateTime)
    stats = database.Column(String)

    def __init__(self, date: datetime.datetime, stats: str):
        self.date = date
        self.stats = stats

    def __repr__(self):
        return f"<Statistic: {self.date}: {self.stats}>"

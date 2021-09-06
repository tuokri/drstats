import datetime

from flask_sqlalchemy import Model
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String


class Statistic(Model):
    __tablename__ = "Statistics"

    # server_addr = Column(String(15))
    date = Column("date", DateTime)
    stats = Column("stats", String)

    def __init__(self, date: datetime.datetime, stats: str):
        self.date = date
        self.stats = stats

    def __repr__(self):
        return f"<Statistic: {self.date}: {self.stats}>"

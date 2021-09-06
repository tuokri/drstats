import datetime

from app import db


class Statistic(db.Model):
    __tablename__ = "Statistics"

    # server_addr = Column(String(15))
    date = db.Column("date", db.DateTime)
    stats = db.Column("value", db.String)

    def __init__(self, date: datetime.datetime, stats: str):
        self.date = date
        self.stats = stats

    def __repr__(self):
        return f"<Statistic: {self.date}: {self.stats}>"

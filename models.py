import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Statistic(db.Model):
    __tablename__ = "Statistics"

    # server_addr = Column(String(15))
    ident = db.Column("ident", db.Sequence(name="ident", start=1, increment=1))
    date = db.Column("date", db.DateTime)
    stats = db.Column("stats", db.String)

    def __init__(self, date: datetime.datetime, stats: str):
        self.date = date
        self.stats = stats

    def __repr__(self):
        return f"<Statistic: {self.date}: {self.stats}>"

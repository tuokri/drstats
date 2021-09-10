from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Server(db.Model):
    """A game server."""
    __tablename__ = "Servers"

    address = db.Column("address", db.String(15), primary_key=True)
    name = db.Column("name", db.String(128), primary_key=True)

    end_game_statistics = relationship("EndGameStatistic", back_populates="server")


class Level(db.Model):
    """A playable level AKA a map."""
    __tablename__ = "Levels"

    name = db.Column("name", db.String(128), primary_key=True)
    version = db.Column("version", db.Integer, primary_key=True)

    obj_infos = relationship("ObjectiveInfo", back_populates="level")
    end_game_statistics = relationship("EndGameStatistic", back_populates="level")


class EndGameStatistic(db.Model):
    """Statistics at the end of the game."""
    __tablename__ = "EndGameStatistics"

    # Dummy column to satisfy SQLAlchemy PK requirement.
    ident = db.Column(
        "ident", db.Integer,
        db.Sequence(name="ident", start=1, increment=1), primary_key=True)

    server_address = db.Column("address", db.String(15), nullable=False)
    server_name = db.Column("name", db.String(128), nullable=False)

    level_name = db.Column("levelName", db.String(128), nullable=False)
    level_version = db.Column("version", db.Integer, nullable=False)

    date = db.Column("date", db.DateTime, nullable=False)
    winning_team = db.Column("winningTeam", db.String(8))
    max_players = db.Column("maxPlayers", db.Integer)
    num_players = db.Column("numPlayers", db.Integer)
    reversed_roles_and_spawns = db.Column("reversedRolesAndSpawns", db.Boolean)
    time_remaining_secs = db.Column("timeRemainingSecs", db.Integer)
    axis_reinforcements = db.Column("axisReinforcements", db.Integer)
    allies_reinforcements = db.Column("alliesReinforcements", db.Integer)
    axis_team_score = db.Column("axisTeamScore", db.Integer)
    allies_team_score = db.Column("alliesTeamScore", db.Integer)

    server = relationship("Server", back_populates="end_game_statistics")
    level = relationship("Level", back_populates="end_game_statistics")

    __table_args__ = (
        ForeignKeyConstraint(
            (server_address, server_name),
            (Server.address, Server.name)),
        ForeignKeyConstraint(
            (level_name, level_version),
            (Level.name, Level.version)),
        {})

    def __repr__(self):
        return f"<Statistic: {self.date}: {self.stats}>"


class ObjectiveInfo(db.Model):
    """Objective status at the end of the game. TODO: Rename?"""
    __tablename__ = "ObjectiveInfos"

    # Dummy column to satisfy SQLAlchemy PK requirement.
    ident = db.Column(
        "ident", db.Integer,
        db.Sequence(name="ident", start=1, increment=1), primary_key=True)

    obj_name = db.Column("objName", db.String(64), primary_key=True)
    obj_index = db.Column("objIndex", db.Integer, primary_key=True)
    obj_state = db.Column("objState", db.Integer)

    level_name = db.Column("name", db.String(128), nullable=False)
    level_version = db.Column("version", db.Integer, nullable=False)

    level = relationship("Level", back_populates="obj_infos")

    __table_args__ = (
        ForeignKeyConstraint(
            (level_name, level_version),
            (Level.name, Level.version)),
        {}
    )

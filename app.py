import os
import re
from collections import defaultdict
from pathlib import Path

import flask
from flask import Flask
from flask import request
from flask import send_from_directory

from models import EndGameStatistic
from models import Level
from models import Server
from models import db

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL").replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] += "?sslmode=require"

db.init_app(app)
with app.app_context():
    db.create_all()
    db.session.commit()

OBJ_INFO_PAT = re.compile(
    r"(<\d\d\?[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/\sÄÖÜäöüß]+>)")

UNKNOWN_ADDRESS = "0.0.0.0"
UNKNOWN_SERVER = "Unknown"

WINBYTE_TO_CONDITION = {
    0: "AllObjectiveCaptured",
    1: "ScoreLimit",
    2: "TimeLimit",
    3: "ReinforcementsDepleted",
    4: "LockDown",
    5: "OverTime",
    6: "MostObjectives",
    7: "BetterTime",
    8: "MostPoints",
    9: "SuddenDeath",
    10: "MatchEndMostRounds",
    11: "MatchEndScoredPoints",
    12: "MatchEndNeutralScoredPoints",
    13: "MatchEndReinforcements",
    14: "MatchEndObjectivesCaptured",
    15: "MatchEndTime",
    16: "MatchEndWonSkirmish",
}


@app.route("/", methods=["GET"])
def index():
    template = (
        """<!doctype html>
        <html>
        <head>
            <link rel="shortcut icon" href="/favicon.ico">
            <title>Desert Rats Statistics</title>
        </head>
        <body>
            {stats}
        </body>
        </html>
        """
    )

    retval = "No statistics"

    all_stats = EndGameStatistic.query

    if all_stats:
        all_stats = all_stats.all()
        if all_stats:
            retval = "\n".join([f"<p>{stat}</p>" for stat in all_stats])

    return template.format(stats=retval)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(Path(app.root_path, "static", "images"),
                               "favicon.ico", mimetype="image/png")


@app.route("/stats", methods=["POST"])
def post_stats():
    """Stats package format:
    DRTE-ElAlamein?164640?500?455?25?1111?8888?<00?Obj1>?<11?Obj2>

    struct BalanceStats
    {
        var string MapName;
        var byte MapVersion;
        var byte WinningTeamName;
        var byte MaxPlayers;
        var byte NumPlayers;
        var byte WinCondition;
        var bool bReverseRolesAndSpawns;
        var int TimeRemainingSeconds;
        var int AxisReinforcements;
        var int AlliesReinforcements;
        var int AxisTeamScore;
        var int AlliesTeamScore;
        var array<ObjectiveInfo> ObjInfos;
    };

    enum EROWinCondition
    {
        ROWC_AllObjectiveCaptured,
        ROWC_ScoreLimit,
        ROWC_TimeLimit,
        ROWC_ReinforcementsDepleted,
        ROWC_LockDown,
        ROWC_OverTime,
        ROWC_MostObjectives,
        ROWC_BetterTime,
        ROWC_MostPoints,
        ROWC_SuddenDeath,
        ROWC_MatchEndMostRounds,
        ROWC_MatchEndScoredPoints,
        ROWC_MatchEndNeutralScoredPoints,
        ROWC_MatchEndReinforcements,
        ROWC_MatchEndObjectivesCaptured,
        ROWC_MatchEndTime,
        ROWC_MatchEndWonSkirmish
    };
    """
    # For Heroku routing only.
    address = request.headers["X-Forwarded-For"]

    data = str(request.data, encoding="latin-1").strip()
    data = data.split("?")

    if len(data) < 10:
        return flask.Response(status=400)

    stats = {}

    map_name = data[0]
    map_version = data[1]

    data_blob = data[2]  # 164640
    team_dict = defaultdict(lambda: "?")
    team_dict[0] = "Axis"
    team_dict[1] = "Allies"
    winning_team = team_dict[int(data_blob[0])]
    max_players = int(data_blob[1:3])
    num_players = int(data_blob[2:4])
    win_condition = WINBYTE_TO_CONDITION[int(data_blob[5])]
    reversed_roles = bool(data_blob[6])

    time_remaining_secs = data[3]
    axis_reinforcements = data[4]
    allies_reinforcements = data[5]
    axis_score = data[6]
    allies_score = data[7]

    obj_infos = "?".join(data[8:])
    print(obj_infos)
    obj_infos = OBJ_INFO_PAT.findall(obj_infos)

    print(map_name)
    print(winning_team)
    print(max_players)
    print(num_players)
    print(win_condition)
    print(reversed_roles)
    print(time_remaining_secs)
    print(axis_reinforcements)
    print(allies_reinforcements)
    print(axis_score)
    print(allies_score)

    # stats["map_name"] = map_name
    stats["winning_team"] = winning_team
    stats["max_players"] = max_players
    stats["num_players"] = num_players
    stats["win_condition"] = win_condition
    stats["reversed_roles"] = reversed_roles
    stats["time_remaining_secs"] = time_remaining_secs
    stats["axis_reinforcements"] = axis_reinforcements
    stats["allies_reinforcements"] = allies_reinforcements
    stats["axis_score"] = axis_score
    stats["allies_score"] = allies_score

    for obj_info in obj_infos:
        obj_info = obj_info.split("?")
        stats[obj_info[0]] = obj_info[1]
        print(obj_info)

    server = Server(address=address, name="TODO_GET_SERVER_NAME")
    db.session.add(server)

    level = Level(name=map_name, version=map_version)
    db.session.add(level)

    egs = EndGameStatistic(server=server, **stats)
    db.session.add(egs)

    db.session.commit()

    return flask.Response(status=201)


if __name__ == "__main__":
    app.run(threaded=True, port=80)

import re

from flask import Flask
from flask import request

app = Flask("drstats")

OBJ_INFO_PAT = re.compile(r"<\d\d\?\w+>")
STATS = []


@app.route("/", methods=["GET"])
def index():
    return "\n".join(STATS)


@app.route("/stats", methods=["POST"])
def post_stats():
    """Stats package format:
    DRTE-ElAlamein?164640?500?455?25?1111?8888?<00?Obj1>?<11?Obj2>

    struct BalanceStats
    {
        var string MapName;
        var byte WinningTeamName;
        var byte MaxPlayers;
        var byte NumPlayers;
        var bool bReverseRolesAndSpawns;
        var int TimeRemainingSeconds;
        var int AxisReinforcements;
        var int AlliesReinforcements;
        var int AxisTeamScore;
        var int AlliesTeamScore;
        var array<ObjectiveInfo> ObjInfos;
    };
    """
    print(request.headers)
    print(request.data)

    data = str(request.data, encoding="latin-1").strip()
    data = data.split("?")

    if len(data) < 8:
        raise ValueError("invalid data package: not enough fields")

    stats = {}

    map_name = data[0]

    data_blob = data[1]  # 164640
    winning_team = "Axis" if int(data_blob[0]) == 0 else "Allies"
    max_players = int(data_blob[1:3])
    num_players = int(data_blob[2:4])
    reversed_roles = bool(data_blob[5])

    time_remaining_secs = data[2]
    axis_reinforcements = data[3]
    allies_reinforcements = data[4]
    axis_score = data[5]
    allies_score = data[6]

    obj_infos = "?".join(data[6:])
    obj_infos = OBJ_INFO_PAT.match(obj_infos)

    print(map_name)
    print(winning_team)
    print(max_players)
    print(num_players)
    print(reversed_roles)
    print(time_remaining_secs)
    print(axis_reinforcements)
    print(allies_reinforcements)
    print(axis_score)
    print(allies_score)

    stats["map_name"] = map_name
    stats["winning_team"] = winning_team
    stats["max_players"] = max_players
    stats["num_players"] = num_players
    stats["reversed_roles"] = reversed_roles
    stats["time_remaining_secs"] = time_remaining_secs
    stats["axis_reinforcements"] = axis_reinforcements
    stats["allies_reinforcements"] = allies_reinforcements
    stats["axis_score"] = axis_score
    stats["allies_score"] = allies_score

    for obj_info in obj_infos.groups():
        obj_info = obj_info.split("?")
        stats[obj_info[0]] = obj_info[1]
        print(obj_info)


if __name__ == "__main__":
    app.run(threaded=True, port=80)
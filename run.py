import re
import socket
import sys
import threading
from collections import defaultdict
from configparser import ConfigParser
from socketserver import StreamRequestHandler
from socketserver import ThreadingTCPServer
from typing import Optional
from typing import Tuple

import discord
import requests
from discord import RequestsWebhookAdapter
from discord import Webhook
from logbook import Logger
from logbook.handlers import RotatingFileHandler
from logbook.handlers import StreamHandler

StreamHandler(
    sys.stdout, level="INFO", bubble=True).push_application()
RotatingFileHandler(
    "drstatsserver.log", level="INFO", bubble=True).push_application()
logger = Logger("drstatsserver")
# logbook.set_datetime_format("local")

OBJ_INFO_PAT = re.compile(r"<\d\d\?\w+>")


class DRStatsServer(ThreadingTCPServer):
    daemon_threads = True

    def __init__(self, *args, stop_event: threading.Event,
                 discord_config: dict, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = stop_event
        self._discord_config = discord_config

    @property
    def stop_requested(self) -> bool:
        return self._stop_event.is_set()

    @property
    def discord_config(self) -> dict:
        return self._discord_config


class DRStatsRequestHandler(StreamRequestHandler):
    def __init__(self, request, client_address, server: DRStatsServer):
        self.server: DRStatsServer = server
        super().__init__(request, client_address, server)

    def execute_webhook(self, ident: str, msg: str):
        embed: Optional[discord.Embed] = None

        webhook_id = self.server.discord_config[ident][0]
        webhook_token = self.server.discord_config[ident][1]
        webhook = Webhook.partial(
            id=webhook_id, token=webhook_token, adapter=RequestsWebhookAdapter()
        )

        if embed is not None:
            logger.info("sending webhook embed for {i}", i=ident)
            webhook.send(embed=embed)

    def handle(self):
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
        try:
            logger.info("connection opened from: {sender}",
                        sender=self.client_address)

            while not self.server.stop_requested:
                data = self.rfile.readline()
                if data.startswith(b"\x00") or not data:
                    logger.info(
                        "received quit request from {sender}, closing connection",
                        sender=self.client_address)
                    break

                logger.debug("raw data: {data}", data=data)
                data = str(data, encoding="latin-1").strip()
                data = data.split("?")

                if len(data) < 8:
                    raise ValueError("invalid data package: not enough fields")

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

                for obj_info in obj_infos.groups():
                    print(obj_info)

                # if ident in self.server.discord_config:
                #   self.execute_webhook(ident, data)
                # else:
                #    logger.error("server unique ID {i} not in Discord config", i=ident)

        except (ConnectionError, socket.error) as e:
            logger.error("{sender}: connection error: {e}",
                         sender=self.client_address, e=e)

        except Exception as e:
            logger.error("error when handling request from {addr}: {e}",
                         addr=self.client_address, e=e)
            logger.exception(e)


def parse_webhook_url(url: str) -> Tuple[int, str]:
    resp = requests.get(url).json()
    _id = int(resp["id"])
    token = resp["token"]
    return _id, token


def load_config() -> dict:
    cp = ConfigParser()
    cp.read("drstatsserver.ini")
    sections = cp.sections()

    ret = defaultdict(dict, cp)
    for section in sections:
        if section.startswith("rs2server"):
            ident = section.split(".")[1]
            url = cp[section].get("webhook_url")
            try:
                ret["discord"][ident] = parse_webhook_url(url)
            except Exception as e:
                logger.error("webhook URL failure for RS2 server ID={i}: {e}",
                             i=ident, e=e)

    return ret


def terminate(stop_event: threading.Event):
    stop_event.set()


def main():
    config = load_config()

    try:
        server_config = config["drstatsserver"]
        port = server_config.getint("port")
        host = server_config["host"]
        if not port:
            logger.error("port not set, exiting...")
            sys.exit(-1)
    except (ValueError, KeyError, AttributeError) as e:
        logger.debug("invalid config: {e}", e=e, exc_info=True)
        logger.error("invalid config, exiting...")
        sys.exit(-1)

    stop_event = threading.Event()
    addr = (host, port)
    server = None
    try:
        server = DRStatsServer(addr, DRStatsRequestHandler, stop_event=stop_event,
                               discord_config=config["discord"])
        logger.info("serving at: {host}:{port}", host=addr[0], port=addr[1])
        logger.info("press CTRL+C to shut down the server")
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("server stop requested")
    finally:
        if server:
            t = threading.Thread(target=terminate, args=(stop_event,))
            t.start()
            t.join()
            server.shutdown()
            server.server_close()

    logger.info("server shut down successfully")


if __name__ == "__main__":
    main()

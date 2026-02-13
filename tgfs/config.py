# TG-FileStream
# Copyright (C) 2025-2026 Deekshith SH

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import argparse
from os import environ
from typing import Optional

from tgfs.utils.config_utils import ConfigBase

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Skipping .env loading.")

parser = argparse.ArgumentParser(
    prog="tg-filestream", description="TG-FileStream server",)
parser.add_argument("--host", help="Bind host")
parser.add_argument("--port", type=int, help="Bind port")
parser.add_argument("--public-url", help="Public base URL")
parser.add_argument("--connection-limit", type=int, help="Max concurrent connections")
parser.add_argument("--db-backend", help="Database server", choices=("mysql", "mongodb"))
parser.add_argument("--no-update", action="store_true", help="Ignore Telegram Updates")
parser.add_argument("--session", help="Name for current instance", default="")
args = parser.parse_args()


class Config(ConfigBase):
    MYSQL_REQUIRED = {"host", "user", "password", "db"}
    MYSQL_CONFIG = {
        "host": (str, None),
        "port": (int, 3306),
        "user": (str, None),
        "password": (str, None),
        "db": (str, None),
        "minsize": (int, 1),
        "maxsize": (int, 5),
    }

    MONGODB_REQUIRED = {"uri"}
    MONGODB_CONFIG = {
        "uri": (str, None),
        "dbname": (str, "TGFS")
    }

    DB_LIST = {
        "mysql": ("MYSQL", MYSQL_CONFIG, MYSQL_REQUIRED),
        "mongodb": ("MONGODB", MONGODB_CONFIG, MONGODB_REQUIRED)
    }

    # ---------- Telegram ----------
    API_ID: int = int(environ["API_ID"])
    API_HASH: str = environ["API_HASH"]
    BOT_TOKEN: str = environ["BOT_TOKEN"]

    BIN_CHANNEL: int = int(environ["BIN_CHANNEL"])
    TOKENS: list[str] = ConfigBase.get_multi_client_tokens()

    # ---------- Server ----------
    HOST: str = args.host or environ.get("HOST", "0.0.0.0")
    PORT: int = args.port or ConfigBase.env_int("PORT", 8080)
    PUBLIC_URL: str = args.public_url or environ.get("PUBLIC_URL", f"http://{HOST}:{PORT}")

    CONNECTION_LIMIT: int = args.connection_limit or ConfigBase.env_int("CONNECTION_LIMIT", 5)

    DEBUG: bool = ConfigBase.env_bool("DEBUG")
    EXT_DEBUG: bool = ConfigBase.env_bool("EXT_DEBUG")

    DOWNLOAD_PART_SIZE: int = ConfigBase.env_int(
        "DOWNLOAD_PART_SIZE", 1024 * 1024
    )

    # ---------- Bot behavior ----------
    NO_UPDATE: bool = args.no_update or ConfigBase.env_bool("NO_UPDATE")
    SEQUENTIAL_UPDATES: bool = ConfigBase.env_bool("SEQUENTIAL_UPDATES")
    FILE_INDEX_LIMIT: int = ConfigBase.env_int("FILE_INDEX_LIMIT", 10)
    MAX_WARNS: int = ConfigBase.env_int("MAX_WARNS", 3)

    ADMIN_IDS: set[int] = {
        int(x)
        for x in environ.get("ADMIN_IDS", "").split(",")
        if x.strip().isdigit()
    }
    ALLOWED_IDS: set[int] = {
        int(x)
        for x in environ.get("ALLOWED_IDS", "").split(",")
        if x.strip().isdigit()
    }
    if ALLOWED_IDS:
        ALLOWED_IDS = ALLOWED_IDS | ADMIN_IDS

    # ---------- DB ----------
    DB_BACKEND: str = args.db_backend or environ.get("DB_BACKEND", "").lower()

    if DB_BACKEND in DB_LIST:
        DB_CONFIG: dict = ConfigBase.load_backend_config(*DB_LIST[DB_BACKEND])
    else:
        raise RuntimeError(
            f"Unsupported DB_BACKEND '{DB_BACKEND}'. "
            f"Valid options: {DB_LIST.keys()}"
        )
    
    SESSION_NAME: str = args.session

    # ---------- Security ----------
    SECRET: Optional[bytes] = None
    BOT_ID: Optional[int] = None

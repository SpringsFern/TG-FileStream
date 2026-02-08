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

from os import environ
from typing import Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Skipping .env loading.")

def _env_bool(key: str, default: bool = False) -> bool:
    val = environ.get(key)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")

def _env_int(key: str, default: int) -> int:
    return int(environ.get(key, default))

def get_multi_client_tokens() -> list[str]:
    """
    Reads:
        MULTI_TOKEN1=...
        MULTI_TOKEN2=...
    """
    prefix = "MULTI_TOKEN"
    tokens: list[tuple[int, str]] = []

    for key, value in environ.items():
        if key.startswith(prefix):
            suffix = key[len(prefix):]
            if suffix.isdigit():
                tokens.append((int(suffix), value))

    tokens.sort(key=lambda x: x[0])
    return [token for _, token in tokens]

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

def load_backend_config(prefix: str, schema: dict[str, tuple[type, Any]], required: set[str]) -> dict[str, Any]:
    """
    Load env vars like:
        MYSQL_HOST
        MYSQL_PORT
        MYSQL_DB
    """
    kwargs: dict[str, Any] = {}
    missing: list[str] = []

    for key, (typ, default) in schema.items():
        env_key = f"{prefix}_{key.upper()}"

        if env_key in environ:
            kwargs[key] = typ(environ[env_key])
        elif default is not None:
            kwargs[key] = default
        else:
            missing.append(env_key)

    if set(missing) & required:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return kwargs

def load_db_config(db_backend: str) -> dict[str, Any]:
    if db_backend == "mysql":
        DB_CONFIG = load_backend_config("MYSQL", MYSQL_CONFIG, MYSQL_REQUIRED)
    elif db_backend == "mongodb":
        DB_CONFIG = load_backend_config("MONGODB", MONGODB_CONFIG, MONGODB_REQUIRED)
    else:
        raise RuntimeError(
            f"Unsupported DB_BACKEND '{db_backend}'. "
            f"Valid options: mysql, mongodb"
        )

    return DB_CONFIG


class Config:
    # ---------- Telegram ----------
    API_ID: int = int(environ["API_ID"])
    API_HASH: str = environ["API_HASH"]
    BOT_TOKEN: str = environ["BOT_TOKEN"]

    BIN_CHANNEL: int = int(environ["BIN_CHANNEL"])

    TOKENS: list[str] = get_multi_client_tokens()

    # ---------- Server ----------
    HOST: str = environ.get("HOST", "0.0.0.0")
    PORT: int = _env_int("PORT", 8080)
    PUBLIC_URL: str = environ.get("PUBLIC_URL", f"http://{HOST}:{PORT}")

    CONNECTION_LIMIT: int = _env_int("CONNECTION_LIMIT", 5)

    DEBUG: bool = _env_bool("DEBUG")
    EXT_DEBUG: bool = _env_bool("EXT_DEBUG")

    # CACHE_SIZE: int = _env_int("CACHE_SIZE", 128)
    DOWNLOAD_PART_SIZE: int = _env_int("DOWNLOAD_PART_SIZE", 1024 * 1024)

    # ---------- Bot behavior ----------
    NO_UPDATE: bool = _env_bool("NO_UPDATE")
    SEQUENTIAL_UPDATES = _env_bool("SEQUENTIAL_UPDATES")
    FILE_INDEX_LIMIT: int = _env_int("FILE_INDEX_LIMIT", 10)
    MAX_WARNS: int = _env_int("MAX_WARNS", 3)

    ADMIN_IDS: set[int] = {
        int(x)
        for x in environ.get("ADMIN_IDS", "").split(",")
        if x.strip().isdigit()
    }

    # ---------- DB ----------
    DB_BACKEND: str = environ.get("DB_BACKEND").lower()
    DB_CONFIG: dict[str, Any] = load_db_config(DB_BACKEND)

    # ---------- Security ----------
    SECRET: Optional[bytes] = None
    BOT_ID: Optional[int] = None
# TG-FileStream
# Copyright (C) 2025 Deekshith SH

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

from os import environ
from typing import List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Skipping .env loading.")

def get_multi_client_tokens() -> List[int]:
    prefix = "MULTI_TOKEN"
    tokens = []
    for key in environ:
        if key.startswith(prefix):
            suffix = key[len(prefix):]
            if suffix.isdigit():
                tokens.append((int(suffix), environ[key]))

    if tokens:
        tokens.sort(key=lambda x: x[0])

    return [token for _, token in tokens]

class Config:
    API_ID: int = int(environ["API_ID"])
    API_HASH: str = environ["API_HASH"]
    BOT_TOKEN: str = environ["BOT_TOKEN"]
    BIN_CHANNEL: int = int(environ["BIN_CHANNEL"])
    HOST: str = environ.get("HOST", "0.0.0.0")
    PORT: int = environ.get("PORT", 8080)
    PUBLIC_URL: str = environ.get("PUBLIC_URL", f"http://{HOST}:{PORT}")
    DEBUG: bool = bool(environ.get("DEBUG", None))
    EXT_DEBUG: bool = bool(environ.get("EXT_DEBUG", None))
    CONNECTION_LIMIT: int = int(environ.get("CONNECTION_LIMIT", 20))
    TOKENS: List[str] = get_multi_client_tokens()
    CACHE_SIZE: int = int(environ.get("CACHE_SIZE", 128))
    DOWNLOAD_PART_SIZE: int = int(environ.get("DOWNLOAD_PART_SIZE", 1024 * 1024))
    NO_UPDATE: bool = bool(environ.get("NO_UPDATE", False))
    TOS: str = ""

    DB_HOST: str = environ["DB_HOST"]
    DB_USER: str = environ["DB_USER"]
    DB_PASS: str = environ["DB_PASS"]
    DB_NAME: str = environ["DB_NAME"]
    DB_PORT: int = int(environ.get("DB_PORT", 3306))

    SECRET: bytes = None
    FILE_INDEX_LIMIT: int = 10
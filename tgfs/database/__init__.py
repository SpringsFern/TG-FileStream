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

from typing import Optional
from tgfs.config import Config
from tgfs.database.database import BaseStorage
from tgfs.database.mysql import MySQLDB

class DB:
    db: Optional[BaseStorage] = MySQLDB()

    @classmethod
    async def init(cls):
        await cls.db.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            db=Config.DB_NAME,
            minsize=1,
            maxsize=5
        )

    @classmethod
    async def close(cls):
        if cls.db is not None:
            await cls.db.close()
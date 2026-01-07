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

import aiomysql

from .file import FileDB
from .user import UserDB
from .group import GroupDB
from .utils import UtilDB

from pathlib import Path

def read_sql_file(path: str) -> list[str]:
    sql = Path(path).read_text(encoding="utf-8")
    statements = []
    buffer = []

    for line in sql.splitlines():
        line = line.strip()
        if not line or line.startswith("--"):
            continue

        buffer.append(line)
        if line.endswith(";"):
            statements.append(" ".join(buffer))
            buffer.clear()

    return statements

class MySQLDB(FileDB, GroupDB, UserDB, UtilDB):
    _pool: aiomysql.Pool

    async def connect(self, *, host: str, port: int = 3306, user: str, password: str,
                          db: str, minsize: int = 1, maxsize: int = 10, autocommit: bool = False,
                          connect_timeout: int = 10) -> None:
        self._pool = await aiomysql.create_pool(
            host=host, port=port, user=user, password=password, db=db,
            minsize=minsize, maxsize=maxsize, autocommit=autocommit,
            connect_timeout=connect_timeout, charset="utf8mb4"
        )

    async def close(self) -> None:
        self._pool.close()
        await self._pool.wait_closed()

    async def init_db(self) -> None:
        statements = read_sql_file("tgfs/database/mysql/schema.sql")

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                for stmt in statements:
                    await cur.execute(stmt)
                await conn.commit()

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

from typing import AsyncGenerator, Optional

import aiomysql

from tgfs.database.database import BaseStorage
from tgfs.utils.types import User


class UserDB(BaseStorage):
    _pool: aiomysql.Pool

    async def get_user(self, user_id: int) -> Optional[User]:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """
                    SELECT user_id, join_date, ban_date, warns, preferred_lang, curt_op, op_id
                    FROM TGUSER WHERE user_id = %s
                    """,
                    (user_id,)
                )
                row = await cur.fetchone()
                if not row:
                    return None
                return User.from_row(row)

    async def add_user(self, user_id: int) -> bool:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        "INSERT IGNORE INTO TGUSER (user_id) VALUES (%s)",
                        (user_id,)
                    )
                    inserted = cur.rowcount > 0
                    await conn.commit()
                    return bool(inserted)
                except Exception:
                    await conn.rollback()
                    raise

    async def upsert_user(self, user: User) -> bool:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        INSERT INTO TGUSER (user_id, join_date, ban_date, warns, preferred_lang, curt_op, op_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s) AS new
                        ON DUPLICATE KEY UPDATE
                          join_date = new.join_date,
                          ban_date = new.ban_date,
                          warns = new.warns,
                          preferred_lang = new.preferred_lang,
                          curt_op = new.curt_op,
                          op_id = new.op_id
                        """,
                        (user.user_id, user.join_date, user.ban_date, user.warns,
                         user.preferred_lang, user.curt_op.value, user.op_id)
                    )
                    await conn.commit()
                    return True
                except Exception:
                    await conn.rollback()
                    raise

    async def delete_user(self, user_id: int) -> bool:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute("DELETE FROM TGUSER WHERE user_id = %s", (user_id,))
                    deleted = cur.rowcount > 0
                    await conn.commit()
                    return bool(deleted)
                except Exception:
                    await conn.rollback()
                    raise

    async def get_users(self) -> AsyncGenerator[User, None]:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT user_id, join_date, ban_date, warns, preferred_lang, curt_op, op_id FROM TGUSER"
                )

                while True:
                    row = await cur.fetchone()
                    if not row:
                        break

                    yield User.from_row(row)

    async def count_users(self) -> int:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT COUNT(*) FROM TGUSER")
                (count,) = await cur.fetchone()
                return int(count)

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

import asyncio
import aiomysql
from typing import AsyncGenerator, Tuple, Optional

from tgfs.types import GroupInfo

class GroupDB:
    _list_lock = asyncio.Lock()

    async def create_group(self, user_id: int, name: str, is_group: bool = True) -> int:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        INSERT INTO FILE_GROUP (user_id, name, is_group)
                        VALUES (%s, %s, %s)
                        """,
                        (user_id, name, is_group)
                    )
                    group_id = cur.lastrowid
                    await conn.commit()
                    return group_id
                except Exception:
                    await conn.rollback()
                    raise

    async def link_file_group(self, group_id: int, file_id: int, order: Optional[int] = None) -> None:
        async with self._list_lock:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    try:
                        if order is None:
                            await cur.execute(
                                """
                                SELECT COALESCE(MAX(order_index), 0) + 1
                                FROM FILE_GROUP_FILE
                                WHERE group_id = %s
                                FOR UPDATE
                                """,
                                (group_id,)
                            )
                            row = await cur.fetchone()
                            order = int(row[0]) if row else 1

                        await cur.execute(
                            """
                            INSERT INTO FILE_GROUP_FILE (group_id, id, order_index)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                              order_index = VALUES(order_index)
                            """,
                            (group_id, file_id, order)
                        )

                        await conn.commit()
                    except Exception:
                        await conn.rollback()
                        raise

    async def get_groups(self, user_id: int, offset: int = 0, limit: Optional[int] = None, is_group: bool = True) -> AsyncGenerator[Tuple[int, str], None]:
        base_sql = """
                    SELECT group_id, name
                    FROM FILE_GROUP
                    WHERE user_id = %s AND is_group = %s
                    ORDER BY created_at DESC
                    """
        params = [user_id]

        if limit is not None:
            base_sql += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.SSCursor) as cur:
                await cur.execute(base_sql, params)
                async for row in cur:
                    group_id, name = row
                    yield int(group_id), str(name)

    async def get_group(self, group_id: int, user_id: int) -> Optional[GroupInfo]:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """
                    SELECT group_id, user_id, name, is_group, created_at
                    FROM FILE_GROUP
                    WHERE group_id = %s AND user_id = %s
                    LIMIT 1
                    """,
                    (group_id, user_id)
                )
                row = await cur.fetchone()
                if not row:
                    return None

                gi = GroupInfo(
                    group_id=int(row["group_id"]),
                    user_id=int(row["user_id"]),
                    name=row["name"],
                    is_group=bool(row["is_group"]),
                    created_at=row.get("created_at"),
                    files=[]
                )

                await cur.execute(
                    """
                    SELECT id
                    FROM FILE_GROUP_FILE
                    WHERE group_id = %s
                    ORDER BY order_index ASC
                    """,
                    (group_id,)
                )
                rows = await cur.fetchall()
                if not rows:
                    return gi

                gi.files.extend([int(r["id"]) for r in rows])
                return gi

    async def delete_group(self, group_id: int, user_id: int) -> None:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        DELETE FROM FILE_GROUP
                        WHERE group_id = %s AND user_id = %s
                        """,
                        (group_id, user_id)
                    )
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise

    async def update_group_name(self, group_id: int, user_id: int, name: str) -> None:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        UPDATE FILE_GROUP
                        SET name = %s
                        WHERE group_id = %s AND user_id = %s
                        """,
                        (name, group_id, user_id)
                    )
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise

    async def update_group_order(self, group_id: int, file_id: int, user_id: int, new_order: int) -> None:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        UPDATE FILE_GROUP_FILE gff
                        JOIN FILE_GROUP fg
                          ON fg.group_id = gff.group_id
                        SET gff.order_index = %s
                        WHERE gff.group_id = %s
                          AND gff.id = %s
                          AND fg.user_id = %s
                        """,
                        (new_order, group_id, file_id, user_id)
                    )
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise

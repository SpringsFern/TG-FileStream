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

import datetime
import aiomysql
from typing import AsyncGenerator, Tuple, Optional

from pyparsing import Union
from telethon.tl.types import InputDocumentFileLocation, InputPhotoFileLocation

from tgfs.types import FileSource, GroupInfo, FileInfo, InputTypeLocation

class FileDB:
    async def add_file(self, file: FileInfo) -> None:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        INSERT INTO FILE (id, dc_id, size, mime_type, file_name, thumb_size, is_deleted)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                          dc_id = VALUES(dc_id),
                          size = VALUES(size),
                          mime_type = VALUES(mime_type),
                          file_name = VALUES(file_name),
                          thumb_size = VALUES(thumb_size)
                        """,
                        (
                            file.id, file.dc_id, file.file_size, file.mime_type,
                            file.file_name, file.thumb_size,
                            file.is_deleted
                        )
                    )
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise

    async def link_user_file(self, file_id: int, user_id: int, msg_id: int, chat_id: Optional[int]) -> None:
        chat_id = chat_id or user_id
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    if user_id is not None:
                        await cur.execute(
                            """
                            INSERT INTO USER_FILE (user_id, id, source_chat_id, source_msg_id)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                              source_chat_id = COALESCE(VALUES(source_chat_id), source_chat_id),
                              source_msg_id = COALESCE(VALUES(source_msg_id), source_msg_id)
                            """,
                            (user_id, file_id, chat_id, msg_id)
                        )

                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise

    async def get_file(self, file_id: int) -> Optional[FileInfo]:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """
                    SELECT id AS file_id,
                           dc_id, size AS file_size, mime_type, file_name, thumb_size, is_deleted
                    FROM FILE
                    WHERE id = %s
                    LIMIT 1
                    """,
                    (file_id, )
                )
                row = await cur.fetchone()
                if not row:
                    return None

                return FileInfo(
                    id = int(row["file_id"]),
                    dc_id = int(row["dc_id"]),
                    file_size = int(row["file_size"]),
                    mime_type = row["mime_type"],
                    file_name = row["file_name"],
                    thumb_size = row["thumb_size"],
                    is_deleted = bool(row["is_deleted"])
                )
            
    async def get_location(self, file: FileInfo, bot_id: int) -> Optional[InputTypeLocation]:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """
                    SELECT access_hash, file_reference
                    FROM FILE_LOCATION
                    WHERE id = %s and bot_id = %s
                    LIMIT 1
                    """,
                    (file.id, bot_id)
                )
                row = await cur.fetchone()
                if not row:
                    return None
                
                cls = InputPhotoFileLocation if file.thumb_size else InputDocumentFileLocation
                return cls(
                    id=file.id,
                    access_hash=int(row["access_hash"]),
                    file_reference=row["file_reference"],
                    thumb_size=file.thumb_size
                ) 

    async def get_source(self, file_id: int, user_id: int) -> Optional[FileSource] :
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """
                    SELECT source_chat_id, source_msg_id, added_at
                    FROM USER_FILE 
                    WHERE id = %s and user_id = %s
                    LIMIT 1
                    """,
                    (file_id, user_id)
                )
                row = await cur.fetchone()
                if not row:
                    return None
                return FileSource(
                    chat_id = int(row["source_chat_id"]),
                    message_id = int(row["source_msg_id"]),
                    time = row["added_at"]
                )

    async def upsert_location(self, bot_id: int, loc: InputTypeLocation) -> None:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        INSERT INTO FILE_LOCATION (bot_id, id, access_hash, file_reference)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                          access_hash = VALUES(access_hash),
                          file_reference = VALUES(file_reference)
                        """,
                        (bot_id, loc.id, loc.access_hash, loc.file_reference)
                    )
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise

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

    async def get_groups(self, user_id: int, is_group: bool = True) -> AsyncGenerator[Tuple[int, str], None]:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.SSCursor) as cur:
                await cur.execute(
                    """
                    SELECT group_id, name
                    FROM FILE_GROUP
                    WHERE user_id = %s AND is_group = %s
                    ORDER BY created_at DESC
                    """,
                    (user_id, is_group)
                )
                while True:
                    row = await cur.fetchone()
                    if not row:
                        break
                    group_id, name = row
                    yield (group_id, name)

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

    async def get_files(self, user_id: int) -> AsyncGenerator[Tuple[int, str], None]:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.SSCursor) as cur:
                await cur.execute(
                    """
                    SELECT f.id AS file_id, f.file_name
                    FROM FILE f join USER_FILE uf ON f.id = uf.id
                    WHERE uf.user_id = %s
                    ORDER BY uf.added_at DESC
                    """,
                    (user_id,)
                )
                while True:
                    row = await cur.fetchone()
                    if not row:
                        break
                    file_id, file_name = row
                    yield (int(file_id), str(file_name))

    async def total_files(self, user_id: int, is_group: Optional[bool] = None) -> int:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                if is_group is None:
                    await cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM USER_FILE
                        WHERE user_id = %s
                        """,
                        (user_id,)
                    )
                else:
                    await cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM FILE_GROUP
                        WHERE user_id = %s AND is_group = %s
                        """,
                        (user_id, is_group)
                    )

                row = await cur.fetchone()
                return int(row[0]) if row else 0


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
from typing import AsyncGenerator, Optional

from telethon.tl.types import InputDocumentFileLocation, InputPhotoFileLocation

from tgfs.database.database import BaseStorage
from tgfs.utils.types import FileSource, FileInfo, InputTypeLocation

class FileDB(BaseStorage):
    async def add_file(self, user_id: int, file: FileInfo, source: FileSource) -> None:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        INSERT INTO TGFILE (id, dc_id, size, mime_type, file_name, thumb_size, is_deleted)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                          dc_id = VALUES(dc_id),
                          size = VALUES(size),
                          mime_type = VALUES(mime_type),
                          file_name = VALUES(file_name),
                          thumb_size = VALUES(thumb_size),
                          is_deleted = VALUES(is_deleted)
                        """,
                        (
                            file.id, file.dc_id, file.file_size, file.mime_type,
                            file.file_name, file.thumb_size,
                            file.is_deleted
                        )
                    )
                    await cur.execute(
                        """
                        INSERT INTO USER_FILE (user_id, id, source_chat_id, source_msg_id)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                          source_chat_id = COALESCE(VALUES(source_chat_id), source_chat_id),
                          source_msg_id = COALESCE(VALUES(source_msg_id), source_msg_id)
                        """,
                        (user_id, file.id, source.chat_id, source.message_id)
                    )
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise

    async def update_file_restriction(self, file_id: int, status: bool) -> None:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        UPDATE TGFILE SET is_deleted = %s WHERE id = %s
                        """,
                        (status, file_id)
                    )
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise

    async def get_file(self, file_id: int, user_id: Optional[int] = None) -> Optional[FileInfo]:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if user_id is None:
                    await cur.execute(
                        """
                        SELECT f.id AS file_id,
                               f.dc_id,
                               f.size AS file_size,
                               f.mime_type,
                               f.file_name,
                               f.thumb_size,
                               f.is_deleted
                        FROM TGFILE f
                        WHERE f.id = %s
                        LIMIT 1
                        """,
                        (file_id, )
                    )
                else:
                    await cur.execute(
                        """
                        SELECT f.id AS file_id,
                               f.dc_id,
                               f.size AS file_size,
                               f.mime_type,
                               f.file_name,
                               f.thumb_size,
                               f.is_deleted
                        FROM TGFILE f
                        WHERE f.id = %s
                        AND EXISTS (
                            SELECT 1
                            FROM USER_FILE uf
                            WHERE uf.id = f.id
                              AND uf.user_id = %s
                        )
                        LIMIT 1
                        """,
                        (file_id, user_id)
                    )
    
                row = await cur.fetchone()
                if not row:
                    return None
    
                return FileInfo(
                    id=int(row["file_id"]),
                    dc_id=int(row["dc_id"]),
                    file_size=int(row["file_size"]),
                    mime_type=row["mime_type"],
                    file_name=row["file_name"],
                    thumb_size=row["thumb_size"],
                    is_deleted=bool(row["is_deleted"]),
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

    async def get_files(self, user_id: int, offset: int = 0, limit: Optional[int] = None
    ) -> AsyncGenerator[tuple[int, str], None]:

        base_sql = """
            SELECT f.id AS file_id, f.file_name
            FROM TGFILE f
            JOIN USER_FILE uf ON f.id = uf.id
            WHERE uf.user_id = %s
            ORDER BY uf.added_at DESC
        """

        params = [user_id]

        if limit is not None:
            base_sql += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.SSCursor) as cur:
                await cur.execute(base_sql, params)

                async for row in cur:
                    file_id, file_name = row
                    yield int(file_id), str(file_name)

    async def get_files2(self,user_id: int,file_ids: list[int],full: bool = False,
    ) -> AsyncGenerator[dict | tuple[int, str], None]:

        if not file_ids:
            return

        placeholders = ",".join(["%s"] * len(file_ids))

        if full:
            select_clause = "f.*"
        else:
            select_clause = "f.id AS file_id, f.file_name"

        base_sql = f"""
            SELECT {select_clause}
            FROM TGFILE f
            JOIN USER_FILE uf ON f.id = uf.id
            WHERE uf.user_id = %s
              AND f.id IN ({placeholders})
            ORDER BY uf.added_at DESC
        """

        params = [user_id] + file_ids

        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.SSCursor) as cur:
                await cur.execute(base_sql, params)

                if full:
                    columns = [col[0] for col in cur.description]

                    async for row in cur:
                        yield dict(zip(columns, row))
                else:
                    async for row in cur:
                        file_id, file_name = row
                        yield int(file_id), str(file_name)

    async def get_file_users(self, file_id: int, ) -> set[int]:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT user_id
                    FROM USER_FILE
                    WHERE id = %s
                    """,
                    (file_id)
                )

                rows = await cur.fetchall()
                return {col[0] for col in rows}

    async def total_files(self, user_id: int) -> int:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM USER_FILE
                    WHERE user_id = %s
                    """,
                    (user_id,)
                )

                row = await cur.fetchone()
                return int(row[0]) if row else 0

    async def delete_file(self, file_id: int) -> bool:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                try:
                    await cur.execute(
                        """
                        DELETE FROM TGFILE
                        WHERE id = %s
                        LIMIT 1
                        """,
                        (file_id)
                    )
                    deleted = bool(cur.rowcount > 0)
                    await conn.commit()
                    return deleted
                except Exception:
                    await conn.rollback()
                    raise

    async def remove_file(self, file_id: int, user_id: int) -> bool:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                try:
                    await cur.execute(
                        """
                        DELETE FROM USER_FILE
                        WHERE id = %s AND user_id = %s
                        LIMIT 1
                        """,
                        (file_id, user_id)
                    )
                    deleted = bool(cur.rowcount > 0)
                    await conn.commit()
                    return deleted
                except Exception:
                    await conn.rollback()
                    raise
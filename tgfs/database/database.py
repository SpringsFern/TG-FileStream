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

# from abc import ABC, abstractmethod
import aiomysql
from typing import AsyncGenerator, Optional

from telethon.tl.types import InputDocumentFileLocation, InputPhotoFileLocation

from tgfs.types import FileSource, User, FileInfo, InputTypeLocation

class MySQLDB:
    def __init__(self, pool: aiomysql.Pool):
        self._pool = pool

    @classmethod
    async def create_pool(cls, *, host: str, port: int = 3306, user: str, password: str,
                          db: str, minsize: int = 1, maxsize: int = 10, autocommit: bool = True,
                          connect_timeout: int = 10) -> "MySQLDB":
        pool = await aiomysql.create_pool(
            host=host, port=port, user=user, password=password, db=db,
            minsize=minsize, maxsize=maxsize, autocommit=autocommit,
            connect_timeout=connect_timeout, charset="utf8mb4"
        )
        return cls(pool)

    # async def init_db(self) -> None:
    #     """Create tables if they don't exist."""
    #     async with self._pool.acquire() as conn:
    #         async with conn.cursor() as cur:
    #             await cur.execute(CREATE_USERS_TABLE_SQL)
    #             await conn.commit()

    async def close(self) -> None:
        self._pool.close()
        await self._pool.wait_closed()

    async def get_user(self, user_id: int) -> Optional[User]:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT user_id, join_date, ban_date, warns, preferred_lang FROM USER WHERE user_id = %s", (user_id,))
                row = await cur.fetchone()
                if not row:
                    return None
                return User.from_row(row)


    async def add_user(self, user_id: int) -> bool:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        "INSERT IGNORE INTO USER (user_id) VALUES (%s)",
                        (user_id,)
                    )
                    inserted = cur.rowcount > 0
                    await conn.commit()
                    return bool(inserted)
                except Exception:
                    await conn.rollback()
                    raise

    async def upsert_user(self, user: User) -> None:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        INSERT INTO USER (user_id, join_date, ban_date, warns, preferred_lang)
                        VALUES (%s, %s, %s, %s, %s) AS new
                        ON DUPLICATE KEY UPDATE
                          join_date = new.join_date,
                          ban_date = new.ban_date,
                          warns = new.warns,
                          preferred_lang = new.preferred_lang
                        """,
                        (user.user_id, user.join_date, user.ban_date, user.warns, user.preferred_lang)
                    )
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise

    async def delete_user(self, user_id: int) -> bool:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute("DELETE FROM USER WHERE user_id = %s", (user_id,))
                    deleted = cur.rowcount > 0
                    await conn.commit()
                    return bool(deleted)
                except Exception:
                    await conn.rollback()
                    raise

    async def get_users(self) -> AsyncGenerator[User, None]:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.SSCursor) as cur:
                await cur.execute(
                    "SELECT user_id, join_date, ban_date, warns, preferred_lang FROM users"
                )

                while True:
                    row = await cur.fetchone()
                    if not row:
                        break

                    row_dict = {
                        "user_id": row[0],
                        "join_date": row[1],
                        "ban_date": row[2],
                        "warns": row[3],
                        "preferred_lang": row[4],
                    }

                    yield User.from_row(row_dict)

    async def count_users(self) -> int:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT COUNT(*) FROM users")
                (count,) = await cur.fetchone()
                return int(count)            

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

    async def add_location(self, file_id: int, bot_id: int, access_hash: int, file_reference: bytes) -> None:
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
                        (bot_id, file_id, access_hash, file_reference)
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

    async def get_source(self, file_id: int, user_id: int):
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

    async def upsert_locations(self, bot_id: int, loc: InputTypeLocation) -> None:
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

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

import os

import json
from typing import Optional

from tgfs.database.database import BaseStorage
from tgfs.utils.types import SupportedType

def encode_value(value: SupportedType) -> tuple[bytes, str]:
    if isinstance(value, bytes):
        return value, "bytes"

    if isinstance(value, str):
        return value.encode("utf-8"), "str"

    if isinstance(value, bool):
        return (b"\x01" if value else b"\x00"), "bool"

    if isinstance(value, int):
        size = max(1, (value.bit_length() + 7) // 8)
        return value.to_bytes(size, "big", signed=True), "int"

    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(",", ":")).encode("utf-8"), "json"

    raise TypeError(f"Unsupported type: {type(value)}")

def decode_value(data: bytes, vtype: str) -> SupportedType:
    if vtype == "bytes":
        return data

    if vtype == "str":
        return data.decode("utf-8")

    if vtype == "bool":
        return data != b"\x00"

    if vtype == "int":
        return int.from_bytes(data, "big", signed=True)

    if vtype == "json":
        return json.loads(data.decode("utf-8"))

    raise ValueError(f"Unknown type: {vtype}")


class UtilDB(BaseStorage):
    async def get_secret(self, rotate=False) -> bytes:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                if not rotate:
                    await cur.execute(
                        "SELECT v FROM APP_CONFIG WHERE k = %s",
                        ("link.secret",)
                    )
                    row: bytes = await cur.fetchone()
                    if row:
                        return row[0]

                secret = os.urandom(32)
                await cur.execute(
                    """
                    INSERT INTO APP_CONFIG (k, v)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE
                      v = VALUES(v)
                    """,
                    ("link.secret", secret)
                )

                await conn.commit()
                return secret
            
    async def get_config_value(self, key: str) -> Optional[SupportedType]:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT v, type FROM APP_CONFIG WHERE k = %s",
                    (key,)
                )
                row = await cur.fetchone()
                if not row:
                    return None

                data, vtype = row
                return decode_value(data, vtype)

    async def set_config_value(self, key: str, value: SupportedType) -> None:
        data, vtype = encode_value(value)

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        """
                        INSERT INTO APP_CONFIG (k, v, type)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                          v = VALUES(v),
                          type = VALUES(type)
                        """,
                        (key, data, vtype)
                    )
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise

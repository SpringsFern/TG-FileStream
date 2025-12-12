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
from typing import List, Optional, Union, Any, Dict
from dataclasses import dataclass
from enum import Enum

from telethon.tl import types

InputTypeLocation = Union[types.InputDocumentFileLocation, types.InputPhotoFileLocation]
InputMedia = Union[types.Document, types.Photo, types.PhotoEmpty, types.DocumentEmpty]

class Status(Enum):
    NO_OP=0
    GROUP=1

@dataclass
class FileInfo:
    __slots__ = ("id", "dc_id", "file_size", "mime_type", "file_name", "thumb_size", "is_deleted")
    id: int
    dc_id: int
    file_size: int
    mime_type: str
    file_name: str
    thumb_size: str
    is_deleted: bool

@dataclass
class FileSource:
    __slots__ = ("time", "chat_id", "message_id")
    chat_id: int
    message_id: int
    time: datetime.datetime


@dataclass
class User:
    user_id: int
    join_date: Optional[datetime.datetime] = None
    ban_date: Optional[datetime.datetime] = None
    warns: int = 0
    preferred_lang: str = "en"   # 2-letter ISO code, default en
    curt_op: Optional[Status] = Status.NO_OP
    op_id: Optional[int] = 0

    @property
    def is_banned(self) -> bool:
        return self.ban_date is not None

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "User":

        def parse_dt(val):
            if isinstance(val, datetime.datetime):
                return val
            if isinstance(val, (str, bytes)):
                try:
                    s = val.decode() if isinstance(val, bytes) else val
                    return datetime.datetime.fromisoformat(s)
                except Exception:
                    return None
            return None

        return cls(
            user_id = int(row["user_id"]),
            join_date = parse_dt(row.get("join_date")),
            ban_date = parse_dt(row.get("ban_date")),
            warns = int(row.get("warns", 0)),
            preferred_lang = row.get("preferred_lang") or "en",
            curt_op = Status(row.get("curt_op")),
            op_id = int(row.get("op_id"))
        )
    
@dataclass
class GroupInfo:
    group_id: int
    user_id: int
    name: str
    is_group: bool
    created_at: Optional[datetime.datetime]
    files: Optional[List[int]] = None

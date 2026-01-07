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

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from tgfs.database.database import BaseStorage

from .file import FileDB
from .group import GroupDB
from .user import UserDB
from .utils import UtilDB

class MongoDB(FileDB, GroupDB, UserDB, UtilDB, BaseStorage):
    client: AsyncIOMotorClient
    db: AsyncIOMotorDatabase
    files: AsyncIOMotorCollection
    groups: AsyncIOMotorCollection
    users: AsyncIOMotorCollection
    config: AsyncIOMotorCollection

    async def connect(self, uri: str, dbname) -> None:
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[dbname]

        self.files  = self.db.files
        self.groups = self.db.groups
        self.users  = self.db.users
        self.config = self.db.app_config

    async def close(self) -> None:
        self.client.close()

    async def init_db(self) -> None:
        await self._create_indexes()

    async def _create_indexes(self) -> None:
        await self.files.create_index("users.user_id")
        await self.files.create_index("is_deleted")
        await self.files.create_index("users.added_at")

        await self.groups.create_index("user_id")
        await self.groups.create_index([("user_id", 1), ("created_at", -1)])

        await self.users.create_index("ban_date")
        await self.users.create_index("warns")

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

from motor.motor_asyncio import AsyncIOMotorCollection
from bson.binary import Binary
from pymongo import ReturnDocument

from tgfs.database.database import BaseStorage
from tgfs.types import SUPPORTED_TYPE

class UtilDB(BaseStorage):
    config: AsyncIOMotorCollection
    async def get_secret(self, rotate: bool = False) -> bytes:
        if not rotate:
            doc = await self.config.find_one({"_id": "link.secret"})
            if doc:
                return doc["value"]

        secret = os.urandom(32)

        await self.config.update_one(
            {"_id": "link.secret"},
            {"$set": {"value": Binary(secret)}},
            upsert=True,
        )

        return secret
    
    async def get_config_value(self, key: str):
        doc = await self.config.find_one({"_id": key})
        return doc["value"] if doc else None

    async def set_config_value(self, key: str, value):
        await self.config.update_one(
            {"_id": key},
            {"$set": {"value": value}},
            upsert=True,
        )

    async def group_counter(self) -> int:
        result = await self.config.find_one_and_update(
            {"_id": "group.counter"},
            {"$inc": {"value": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return result["value"]
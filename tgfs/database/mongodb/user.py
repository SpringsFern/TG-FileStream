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

from typing import Optional, AsyncGenerator
from datetime import datetime, timezone

from tgfs.database.database import BaseStorage
from tgfs.types import Status, User

class UserDB(BaseStorage):
    async def get_user(self, user_id: int) -> Optional[User]:
        doc = await self.users.find_one({"_id": user_id})
        if not doc:
            return None

        return User(
            user_id=doc["_id"],
            join_date=doc["join_date"],
            ban_date=doc.get("ban_date"),
            warns=doc["warns"],
            preferred_lang=doc["preferred_lang"],
            curt_op=Status(doc["curt_op"]),
            op_id=doc["op_id"],
        )

    async def add_user(self, user_id: int) -> bool:
        try:
            await self.users.insert_one({
                "_id": user_id,
                "join_date": datetime.now(timezone.utc),
                "ban_date": None,
                "warns": 0,
                "preferred_lang": "en",
                "curt_op": 0,
                "op_id": 0,
            })
            return True
        except Exception:
            return False

    async def upsert_user(self, user: User) -> bool:
        await self.users.update_one(
            {"_id": user.user_id},
            {
                "$set": {
                    "join_date": user.join_date,
                    "ban_date": user.ban_date,
                    "warns": user.warns,
                    "preferred_lang": user.preferred_lang,
                    "curt_op": user.curt_op.value,
                    "op_id": user.op_id,
                }
            },
            upsert=True,
        )
        return True

    async def delete_user(self, user_id: int) -> bool:
        res = await self.users.delete_one({"_id": user_id})
        return res.deleted_count > 0
    
    async def get_users(self) -> AsyncGenerator[User, None]:
        cursor = self.users.find({})

        async for doc in cursor:
            yield User(
                user_id=doc["_id"],
                join_date=doc["join_date"],
                ban_date=doc.get("ban_date"),
                warns=doc["warns"],
                preferred_lang=doc["preferred_lang"],
                curt_op=doc["curt_op"],
                op_id=doc["op_id"],
            )

    async def count_users(self) -> int:
        return await self.users.count_documents({})
    



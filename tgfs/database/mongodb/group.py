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
from datetime import datetime, timezone

from tgfs.database.database import BaseStorage
from tgfs.types import GroupInfo

class GroupDB(BaseStorage):
    async def create_group(self, group_id: int, user_id: int, name: str) -> None:
        await self.groups.insert_one({
            "_id": group_id,
            "user_id": user_id,
            "name": name,
            "created_at": datetime.now(timezone.utc),
            "files": {},
        })

    async def add_file_to_group(
        self,
        group_id: int,
        user_id: int,
        file_id: int,
        order: Optional[int] = None,
    ) -> None:
        if order is None:
            doc = await self.groups.find_one(
                {"_id": group_id, "user_id": user_id},
                {"files": 1},
            )

            order = 1
            if doc and "files" in doc:
                order = len(doc["files"])+1

        await self.groups.update_one(
            {"_id": group_id, "user_id": user_id},
            {
                "$set": {
                    f"files.{file_id}": {"order": order}
                }
            },
            upsert=False,
        )

    async def get_groups(
        self, user_id: int, offset: int = 0, limit: Optional[int] = None
    ) -> AsyncGenerator[tuple[int, str], None]:

        cursor = (
            self.groups.find(
                {"user_id": user_id},
                {"name": 1},
            )
            .sort("created_at", -1)
            .skip(offset)
        )

        if limit is not None:
            cursor = cursor.limit(limit)

        async for doc in cursor:
            yield doc["_id"], doc["name"]

    async def get_group(self, group_id: int, user_id: int) -> Optional[GroupInfo]:
        doc = await self.groups.find_one(
            {"_id": group_id, "user_id": user_id}
        )
        if not doc:
            return None

        files = [
            int(fid)
            for fid, _ in sorted(
                doc.get("files", {}).items(),
                key=lambda i: i[1]["order"]
            )
        ]

        return GroupInfo(
            group_id=doc["_id"],
            user_id=doc["user_id"],
            name=doc["name"],
            created_at=doc["created_at"],
            files=files
        )

    async def delete_group(self, group_id: int, user_id: int) -> None:
        await self.groups.delete_one(
            {"_id": group_id, "user_id": user_id}
        )

    async def update_group_name(self, group_id: int, user_id: int, name: str) -> None:
        await self.groups.update_one(
            {"_id": group_id, "user_id": user_id},
            {"$set": {"name": name}},
        )

    async def update_group_order(
        self, group_id: int, file_id: int, user_id: int, new_order: int
    ) -> None:
        await self.groups.update_one(
            {
                "_id": group_id,
                "user_id": user_id,
                f"files.{file_id}": {"$exists": True},
            },
            {
                "$set": {
                    f"files.{file_id}.order": new_order
                }
            },
        )

    async def total_groups(self, user_id: int) -> int:
        return await self.groups.count_documents(
            {"user_id": user_id}
        )

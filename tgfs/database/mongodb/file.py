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

from datetime import datetime, timezone
from time import timezone
from typing import AsyncGenerator, Optional

from telethon.tl.types import InputDocumentFileLocation, InputPhotoFileLocation

from tgfs.database.database import BaseStorage
from tgfs.types import FileInfo, FileSource, InputTypeLocation

class FileDB(BaseStorage):
    async def add_file(self, user_id: int, file: FileInfo, source: FileSource) -> None:
        await self.files.update_one(
            {"_id": file.id},
            {
                "$set": {
                    "dc_id": file.dc_id,
                    "size": file.file_size,
                    "mime_type": file.mime_type,
                    "file_name": file.file_name,
                    "thumb_size": file.thumb_size,
                    "is_deleted": file.is_deleted,
                },
                "$addToSet": {
                    "users": {
                        "user_id": user_id,
                        "chat_id": source.chat_id,
                        "message_id": source.message_id,
                        "added_at": datetime.now(timezone.utc),
                    }
                },
            },
            upsert=True,
        )

    async def update_file_restriction(self, file_id: int, status: bool) -> None:
        await self.files.update_one(
            {"_id": file_id},
            {"$set": {"is_deleted": status}},
        )

    async def get_file(self, file_id: int, user_id: Optional[int] = None) -> Optional[FileInfo]:
        query = {"_id": file_id}
        if user_id is not None:
            query["users.user_id"] = user_id
    
        doc = await self.files.find_one(query)
        if not doc:
            return None
    
        return FileInfo(
            id=doc["_id"],
            dc_id=doc["dc_id"],
            file_size=doc["size"],
            mime_type=doc.get("mime_type"),
            file_name=doc.get("file_name"),
            thumb_size=doc.get("thumb_size"),
            is_deleted=bool(doc.get("is_deleted", False)),
        )

    async def get_location(self, file: FileInfo, bot_id: int) -> Optional[InputTypeLocation]:
        doc = await self.files.find_one(
            {"_id": file.id, f"location.{bot_id}": {"$exists": True}},
            {f"location.{bot_id}": 1},
        )
        if not doc:
            return None

        loc = doc["location"][str(bot_id)]
        cls = InputPhotoFileLocation if file.thumb_size else InputDocumentFileLocation
        return cls(
            id=file.id,
            access_hash=loc["access_hash"],
            file_reference=loc["file_reference"],
            thumb_size=file.thumb_size,
        )
    
    async def get_source(self, file_id: int, user_id: int) -> Optional[FileSource]:
        doc = await self.files.find_one(
            {"_id": file_id, "users.user_id": user_id},
            {"users.$": 1},
        )
        if not doc:
            return None

        u = doc["users"][0]
        return FileSource(
            chat_id=u["chat_id"],
            message_id=u["message_id"],
            time=u["added_at"],
        )

    async def get_files(
        self, user_id: int, offset: int = 0, limit: Optional[int] = None
    ) -> AsyncGenerator[tuple[int, str], None]:
    
        cursor = self.files.find(
            {"users.user_id": user_id},
            {"file_name": 1},
        ).sort("users.added_at", -1)

        if offset:
            cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        async for doc in cursor:
            yield doc["_id"], doc.get("file_name")

    async def get_file_users(self, file_id: int) -> set[int]:
        doc = await self.files.find_one(
            {"_id": file_id},
            {"users.user_id": 1},
        )
        if not doc:
            return set()

        return {u["user_id"] for u in doc.get("users", [])}

    async def total_files(self, user_id: int) -> int:
        return await self.files.count_documents(
            {"users.user_id": user_id}
        )

    async def delete_file(self, file_id: int) -> bool:
        res = await self.files.delete_one({"_id": file_id})
        return res.deleted_count > 0

    async def remove_file(self, file_id: int, user_id: int) -> bool:
        res = await self.files.update_one(
            {"_id": file_id},
            {"$pull": {"users": {"user_id": user_id}}},
        )
        return res.modified_count > 0

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

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

from tgfs.utils.types import SupportedType, FileInfo, FileSource, GroupInfo, InputTypeLocation, User


class BaseStorage(ABC):
    """
    Abstract base class for storage backends.
    """

    is_connected: bool

    @abstractmethod
    async def connect(self, **kwargs) -> None:
        """
        Establish a connection to the backend.

        Called once during application startup.
        Should raise an exception if the connection fails.
        """
        raise NotImplementedError

    @abstractmethod
    async def close(self, force: bool = False) -> None:
        """
        Close all open connections and release resources.

        Called during graceful shutdown.
        """
        raise NotImplementedError

    @abstractmethod
    async def init_db(self) -> None:
        """Create tables if they don't exist."""
        raise NotImplementedError

    @abstractmethod
    async def add_file(self, user_id: int, file: FileInfo, source: FileSource) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_file_restriction(self, file_id: int, status: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_file(self, file_id: int, user_id: Optional[int] = None) -> Optional[FileInfo]:
        raise NotImplementedError

    @abstractmethod
    async def get_location(self, file: FileInfo, bot_id: int) -> Optional[InputTypeLocation]:
        raise NotImplementedError

    @abstractmethod
    async def get_source(self, file_id: int, user_id: int) -> Optional[FileSource]:
        raise NotImplementedError

    @abstractmethod
    async def upsert_location(self, bot_id: int, loc: InputTypeLocation) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_files(self, user_id: int, offset: int = 0, limit: Optional[int] = None
                        ) -> AsyncGenerator[tuple[int, str], None]:
        raise NotImplementedError

    @abstractmethod
    async def get_files2(self, user_id: int, file_ids: list[int], full: bool = False
                         ) -> AsyncGenerator[tuple[int, str], None]:
        raise NotImplementedError

    @abstractmethod
    async def get_file_users(self, file_id: int, ) -> set[int]:
        raise NotImplementedError

    @abstractmethod
    async def total_files(self, user_id: int) -> int:
        raise NotImplementedError

    @abstractmethod
    async def delete_file(self, file_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def remove_file(self, file_id: int, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def create_group(self, user_id: int, name: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def add_file_to_group(self, group_id: int, user_id: int, file_id: int, order: Optional[int] = None) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_groups(self, user_id: int, offset: int = 0, limit: Optional[int] = None
    ) -> AsyncGenerator[tuple[int, str], None]:
        raise NotImplementedError

    @abstractmethod
    async def get_group(self, group_id: int, user_id: int) -> Optional[GroupInfo]:
        raise NotImplementedError

    @abstractmethod
    async def delete_group(self, group_id: int, user_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_group_name(self, group_id: int, user_id: int, name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_group_order(self, group_id: int, file_id: int, user_id: int, new_order: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def total_groups(self, user_id: int) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, user_id: int) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def add_user(self, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def upsert_user(self, user: User) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_users(self) -> AsyncGenerator[User, None]:
        raise NotImplementedError

    @abstractmethod
    async def count_users(self) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_secret(self, rotate=False) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def get_config_value(self, key: str) -> Optional[SupportedType]:
        raise NotImplementedError

    @abstractmethod
    async def set_config_value(self, key: str, value: SupportedType) -> None:
        raise NotImplementedError

# TG-FileStream
# Copyright (C) 2019 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Modifications made by Deekshith SH, 2025
# Copyright (C) 2025 Deekshith SH

# pylint: disable=protected-access

import copy
from collections import OrderedDict
from typing import AsyncGenerator, Dict, Optional, List
from contextlib import asynccontextmanager
from dataclasses import dataclass
import logging
import asyncio
import math

from telethon import TelegramClient
from telethon.crypto import AuthKey
from telethon.network import MTProtoSender
from telethon.tl.alltlobjects import LAYER
from telethon.tl.functions import InvokeWithLayerRequest
from telethon.tl.functions.auth import ExportAuthorizationRequest, ImportAuthorizationRequest
from telethon.tl.functions.upload import GetFileRequest
from telethon.tl.types import DcOption
from telethon.errors import DcIdInvalidError, FloodWaitError

from tgfs.config import Config
from tgfs.utils import get_fileinfo, FileInfo, InputTypeLocation

root_log = logging.getLogger(__name__)

if Config.CONNECTION_LIMIT > 25:
    root_log.warning("The connection limit should not be set above 25 to avoid"
                     " infinite disconnect/reconnect loops")


@dataclass
class Connection:
    log: logging.Logger
    sender: MTProtoSender
    lock: asyncio.Lock
    users: int = 0


class DCConnectionManager:
    log: logging.Logger
    client: TelegramClient

    dc_id: int
    dc: Optional[DcOption]
    auth_key: Optional[AuthKey]
    connections: List[Connection]

    _list_lock: asyncio.Lock

    def __init__(self, client: TelegramClient, dc_id: int, log: logging.Logger) -> None:
        self.log = log.getChild(f"dc{dc_id}")
        self.client = client
        self.dc_id = dc_id
        self.auth_key = None
        self.connections = []
        self._list_lock = asyncio.Lock()
        self.dc = None

    async def _new_connection(self) -> Connection:
        if not self.dc:
            self.dc = await self.client._get_dc(self.dc_id)
        sender = MTProtoSender(self.auth_key, loggers=self.client._log)
        index = len(self.connections) + 1
        conn = Connection(sender=sender, log=self.log.getChild(
            f"conn{index}"), lock=asyncio.Lock())
        self.connections.append(conn)
        async with conn.lock:
            conn.log.info("Connecting...")
            connection_info = self.client._connection(self.dc.ip_address, self.dc.port, self.dc.id,
                                                      loggers=self.client._log,
                                                      proxy=self.client._proxy)
            await sender.connect(connection_info)
            if not self.auth_key:
                await self._export_auth_key(conn)
            return conn

    async def _export_auth_key(self, conn: Connection) -> None:
        self.log.info(f"Exporting auth to DC {self.dc.id}"
                      f" (main client is in {self.client.session.dc_id})")
        try:
            auth = await self.client(ExportAuthorizationRequest(self.dc.id))
        except DcIdInvalidError:
            self.log.debug("Got DcIdInvalidError")
            self.auth_key = self.client.session.auth_key
            conn.sender.auth_key = self.auth_key
            return
        init_request = copy.copy(self.client._init_request)
        init_request.query = ImportAuthorizationRequest(
            id=auth.id, bytes=auth.bytes
        )
        req = InvokeWithLayerRequest(
            LAYER, init_request
        )
        await conn.sender.send(req)
        self.auth_key = conn.sender.auth_key

    async def _next_connection(self) -> Connection:
        best_conn: Optional[Connection] = None
        for conn in self.connections:
            if not best_conn or conn.users < best_conn.users:
                best_conn = conn
        if (not best_conn or best_conn.users > 0) and len(self.connections) < Config.CONNECTION_LIMIT:
            best_conn = await self._new_connection()
        return best_conn

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Connection, None]:
        async with self._list_lock:
            conn: Connection = await asyncio.shield(self._next_connection())
            # The connection is locked so reconnections don't stack
            async with conn.lock:
                conn.users += 1
        try:
            yield conn
        finally:
            conn.users -= 1

    async def disconnect(self) -> None:
        async with self._list_lock:
            await asyncio.gather(*[conn.sender.disconnect() for conn in self.connections])


class ParallelTransferrer:
    log: logging.Logger
    client: TelegramClient
    dc_managers: Dict[int, DCConnectionManager]
    users: int
    active_clients: int
    cached_files: OrderedDict[int, asyncio.Task[FileInfo]]

    def __init__(self, client: TelegramClient, client_id: int) -> None:
        self.log = root_log.getChild(f"bot{client_id}")
        self.client = client
        self.users = 0
        self.active_clients = 0
        self.cached_files = OrderedDict()
        self.dc_managers = {
            1: DCConnectionManager(client, 1, self.log),
            2: DCConnectionManager(client, 2, self.log),
            3: DCConnectionManager(client, 3, self.log),
            4: DCConnectionManager(client, 4, self.log),
            5: DCConnectionManager(client, 5, self.log),
        }

    def post_init(self) -> None:
        self.dc_managers[self.client.session.dc_id].auth_key = self.client.session.auth_key

    async def close_connection(self) -> None:
        task = []
        for dcid, dcm in self.dc_managers.items():
            if dcm.connections:
                self.log.debug("Closing connections for DC %d", dcid)
                task.append(dcm.disconnect())
        if task:
            await asyncio.gather(*task)
        self.log.debug("All DC connections closed")

    # is this the best approach? 
    # No
    async def get_file(self, message_id: int, file_name: str) -> Optional[FileInfo]:
        if message_id in self.cached_files:
            file = await self.cached_files[message_id]
            return file if file and file.file_name == file_name else None
        task = asyncio.create_task(get_fileinfo(self.client, message_id, file_name))
        if Config.CACHE_SIZE is not None and len(self.cached_files) > Config.CACHE_SIZE:
            self.cached_files.popitem(last=False)
        self.cached_files[message_id] = task
        file_id = await task
        if not file_id:
            self.cached_files.pop(message_id)
            self.log.debug("File not found for message with ID %s", message_id)
            return None
        self.log.debug("Generated file ID for message with ID %s", message_id)
        return file_id

    async def _int_download(self, request: GetFileRequest, first_part: int, last_part: int,
        part_count: int, part_size: int, dc_id: int, first_part_cut: int,
        last_part_cut: int) -> AsyncGenerator[bytes, None]:
        log = self.log
        self.users += 1
        try:
            part = first_part
            dcm = self.dc_managers[dc_id]
            async with dcm.get_connection() as conn:
                log = conn.log
                while part <= last_part:
                    result = await self.client._call(conn.sender, request)

                    if not result.bytes:
                        break

                    request.offset += part_size
                    if last_part == first_part:
                        yield result.bytes[first_part:last_part]
                    elif part == first_part:
                        yield result.bytes[first_part_cut:]
                    elif part == last_part:
                        yield result.bytes[:last_part_cut]
                    else:
                        yield result.bytes
                    log.debug("Part %d/%d (total %d) downloaded", part, last_part, part_count)
                    part += 1
                log.info("Parallel download finished")
        except (GeneratorExit, StopAsyncIteration, asyncio.CancelledError):
            log.info("Parallel download interrupted")
            raise
        except Exception:
            log.error("Parallel download errored", exc_info=True)
        finally:
            self.active_clients -= 1
            self.users -= 1

    def download(self, location: InputTypeLocation, dc_id: int, file_size: int, offset: int, limit: int
                 ) -> AsyncGenerator[bytes, None]:
        part_size = Config.DOWNLOAD_PART_SIZE
        first_part_cut = offset % part_size
        first_part = math.floor(offset / part_size)
        last_part_cut = (limit % part_size) + 1
        last_part = math.ceil(limit / part_size)
        part_count = math.ceil(file_size / part_size)
        self.log.info("Starting parallel download: chunks %d-%d of %d %s",
                       first_part, last_part, part_count, location)
        request = GetFileRequest(location, offset=first_part * part_size, limit=part_size)

        return self._int_download(request, first_part, last_part, part_count, part_size, dc_id,
                                  first_part_cut, last_part_cut)

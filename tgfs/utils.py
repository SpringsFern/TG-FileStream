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

from typing import cast

from telethon.utils import get_input_location
from telethon.tl.custom import Message

from tgfs.config import Config
from tgfs.paralleltransfer import ParallelTransferrer
from tgfs.types import FileSource, InputTypeLocation
from tgfs.telegram import client
from tgfs.database import DB

async def update_location(source: FileSource, transfer: ParallelTransferrer) -> InputTypeLocation:
    message = cast(Message, await client.forward_messages(Config.BIN_CHANNEL, source.message_id, source.chat_id, drop_author=True))
    msg = cast(Message, await transfer.client.get_messages(message.chat_id, ids=message.id))
    _, location = get_input_location(msg)
    await DB.db.upsert_location(transfer.client_id, location)
    return location


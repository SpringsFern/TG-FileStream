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

import re
import logging

from telethon import events
from telethon.custom import Message
from telethon.tl.types import InputMediaDocument, InputMediaPhoto

from tgfs.config import Config
from tgfs.telegram import client
from tgfs.database import DB
from tgfs.types import User
from tgfs.utils import parse_token

log = logging.getLogger(__name__)

async def send_file(evt: events.NewMessage.Event, user_id: int, file_id: int) -> None:
    file_info = await DB.db.get_file(file_id, user_id)
    if file_info is None:
        return "File with id `{}` not found.".format(file_id)
    location = await DB.db.get_location(file_info, Config.BOT_ID)
    if not location:
        return "File location not found."
    input_media = InputMediaPhoto(location) if location.thumb_size else InputMediaDocument(location)
    await client.send_file(user_id, input_media, caption=file_info.file_name)

async def handle_file_url(evt: events.NewMessage.Event, user: User, match: re.Match) -> None:
    payload = match.group("payload")
    sig = match.group("sig")
    pt = parse_token(payload, sig)
    if not pt:
        await evt.reply("Invalid link.")
        return
    user_id, file_id = pt
    status = await send_file(evt, user_id, file_id)
    if status:
        await evt.reply(status)

async def handle_group_url(evt: events.NewMessage.Event, user: User, match: re.Match) -> None:
    payload = match.group("payload")
    sig = match.group("sig")
    pt = parse_token(payload, sig)
    if not pt:
        await evt.reply("Invalid link.")
        return
    user_id, group_id = pt
    group = await DB.db.get_group(group_id, user_id)
    for file_id in group.files:
        status = await send_file(evt, user_id, file_id)
        if status:
            await evt.reply(status)
    await evt.reply("End of group files.")

HANDLERS = [
    (re.compile(r"^(?P<scheme>https?):\/\/(?P<host>(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|\d{1,3}(?:\.\d{1,3}){3})(?::(?P<port>\d{1,5}))?\/dl\/(?P<payload>[^\/]+)\/(?P<sig>[^\/]+)$"), handle_file_url),
    (re.compile(r"^(?P<scheme>https?):\/\/(?P<host>(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|\d{1,3}(?:\.\d{1,3}){3})(?::(?P<port>\d{1,5}))?\/group\/(?P<payload>[^\/]+)\/(?P<sig>[^\/]+)$"), handle_group_url)
]
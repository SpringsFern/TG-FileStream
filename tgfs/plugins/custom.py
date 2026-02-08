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
from telethon.tl.types import InputMediaDocument, InputMediaPhoto

from tgfs.config import Config
from tgfs.telegram import client
from tgfs.database import DB
from tgfs.utils.translation import get_lang
from tgfs.utils.types import User
from tgfs.utils.utils import parse_token

log = logging.getLogger(__name__)


async def send_file(_: events.NewMessage.Event, user_id: int, file_id: int) -> None:
    lang = get_lang(user_id)
    file_info = await DB.db.get_file(file_id, user_id)
    if file_info is None:
        return lang.FILE_ID_NOT_FOUND.format(file_id=file_id)
    location = await DB.db.get_location(file_info, Config.BOT_ID)
    input_media = InputMediaPhoto(
        location) if location.thumb_size else InputMediaDocument(location)
    await client.send_file(user_id, input_media, caption=file_info.file_name)


async def handle_file_url(evt: events.NewMessage.Event, user: User, match: re.Match) -> None:
    lang = get_lang(user)
    payload = match.group("payload")
    sig = match.group("sig")
    pt = parse_token(payload, sig)
    if not pt:
        await evt.reply(lang.INAVLID_LINK_TEXT)
        return
    user_id, file_id = pt
    status = await send_file(evt, user_id, file_id)
    if status:
        await evt.reply(status)


async def handle_group_url(evt: events.NewMessage.Event, user: User, match: re.Match) -> None:
    lang = get_lang(user)
    payload = match.group("payload")
    sig = match.group("sig")
    pt = parse_token(payload, sig)
    if not pt:
        await evt.reply(lang.INAVLID_LINK_TEXT)
        return
    user_id, group_id = pt
    group = await DB.db.get_group(group_id, user_id)
    for file_id in group.files:
        status = await send_file(evt, user_id, file_id)
        if status:
            await evt.reply(status)
    await evt.reply(lang.GROUP_ENDOF_FILES)

HANDLERS = [
    (re.compile(
        r"^(?P<scheme>https?):\/\/(?P<host>(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|\d{1,3}(?:\.\d{1,3}){3})(?::(?P<port>\d{1,5}))?\/dl\/(?P<payload>[^\/]+)\/(?P<sig>[^\/]+)$"), handle_file_url),
    (re.compile(
        r"^(?P<scheme>https?):\/\/(?P<host>(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|\d{1,3}(?:\.\d{1,3}){3})(?::(?P<port>\d{1,5}))?\/group\/(?P<payload>[^\/]+)\/(?P<sig>[^\/]+)$"), handle_group_url)
]

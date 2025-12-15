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

import logging
from typing import List, Tuple, cast

from telethon import events, Button
from telethon.custom import Message
from telethon.utils import get_input_location

from tgfs.config import Config
from tgfs.telegram import client, multi_clients
from tgfs.database import DB
from tgfs.types import FileInfo, InputTypeLocation, Status
from tgfs.utils import check_get_user

log = logging.getLogger(__name__)

@client.on(events.NewMessage(incoming=True, pattern=r"^\/myfiles", func=lambda x: x.is_private and not x.file))
async def handle_done_command(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    total_files = await DB.db.total_files(user.user_id)
    if total_files == 0:
        await evt.reply("You have not generated a link for any files yet.")
        return
    files_gen = DB.db.get_files(user.user_id)
    files_btn: List[List[Button]] = []
    async for file_id, file_name in files_gen:
        files_btn.append([
            Button.inline(file_name, data=f"fileinfo_{file_id}")
        ])

    await evt.reply(
        f"You have {total_files} files:",
        buttons=files_btn
    )

@client.on(events.NewMessage(incoming=True, pattern=r"^\/mygroups", func=lambda x: x.is_private and not x.file))
async def handle_done_command(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    total_files = await DB.db.total_files(user.user_id, is_group=True)
    if total_files == 0:
        await evt.reply("You have not generated a link for any files yet.")
        return
    files_gen = DB.db.get_groups(user.user_id)
    files_btn: List[List[Button]] = []
    async for file_id, file_name in files_gen:
        files_btn.append([
            Button.inline(file_name, data=f"groupinfo_{file_id}")
        ])

    await evt.reply(
        f"You have {total_files} groups:",
        buttons=files_btn
    )

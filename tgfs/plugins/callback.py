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
from typing import List

from telethon import Button, events

from tgfs.config import Config
from tgfs.telegram import client
from tgfs.database import DB
# from tgfs.plugins.message import handle_file_message

log = logging.getLogger(__name__)

@client.on(events.CallbackQuery(pattern=r"^tos_agree_[1-9]\d{0,19}$"))
async def handle_buttons(evt: events.CallbackQuery.Event):
    callback_data = evt.data.decode('utf-8')
    log.debug("Callback data: %s", callback_data)
    user_id = evt.sender_id
    if not await DB.db.add_user(user_id):
        await evt.answer("Something went wrong")
        return
    # msg = await client.get_messages(user_id, ids=msg_id)
    # await handle_file_message(evt, msg)
    await evt.answer("You have agreed to the Terms of Service.")
    await evt.edit(buttons=[[Button.inline("Agreed", b"tos_agreed")]])

@client.on(events.CallbackQuery(pattern=r"^fileinfo$"))
async def handle_done_command(evt: events.CallbackQuery.Event) -> None:
    user_id = evt.sender_id
    total_files = await DB.db.total_files(user_id)
    if total_files == 0:
        await evt.reply("You have not generated a link for any files yet.")
        return
    files_gen = DB.db.get_files(user_id)
    files_btn: List[List[Button]] = []
    async for file_id, file_name in files_gen:
        files_btn.append([
            Button.inline(file_name, data=f"fileinfo_{file_id}")
        ])

    await evt.edit(
        f"You have {total_files} files:",
        buttons=files_btn
    )

@client.on(events.CallbackQuery(pattern=r"^fileinfo_(\d+)$"))
async def handle_buttons(evt: events.CallbackQuery.Event):
    file_id = int(evt.pattern_match.group(1))
    user_id = evt.sender_id
    file_info = await DB.db.get_file(file_id, user_id)
    if file_info is None:
        await evt.answer("File not found.")
        return
    await evt.edit(
        f"File Info:\n"
        f"ID: {file_info.id}\n"
        f"DC ID: {file_info.dc_id}\n"
        f"Size: {file_info.file_size} bytes\n"
        f"MIME Type: {file_info.mime_type}\n"
        f"File Name: {file_info.file_name}\n"
        f"File Type: {'Photo' if file_info.thumb_size else 'Document'}\n"
        f"Is Restricted: {'Yes' if file_info.is_deleted else 'No'}",
        buttons=[
            [Button.url(file_info.file_name, f"{Config.PUBLIC_URL}/dl/{user_id}/{file_info.id}")],
            [Button.inline("Back", b"fileinfo")]
        ]
    )

@client.on(events.CallbackQuery(pattern=r"^groupinfo_(\d+)$"))
async def handle_buttons(evt: events.CallbackQuery.Event):
    file_id = int(evt.pattern_match.group(1))
    user_id = evt.sender_id
    file_info = await DB.db.get_group(file_id, user_id)
    if file_info is None:
        await evt.answer("Group not found.")
        return
    buttons: List[List[Button]] = []
    for file_id in file_info.files or []:
        buttons.append([Button.inline(str(file_id), f"fileinfo_{file_id}")])
    buttons.append([Button.url("Open", f"{Config.PUBLIC_URL}/group/{user_id}/{file_info.group_id}")])
    await evt.edit(
        f"Group Info:\n"
        f"Name: {file_info.name}\n"
        f"created_at: {file_info.created_at}\n"
        f"Total Files: {len(file_info.files) if file_info.files else 0}",
        buttons=buttons
    )
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
from tgfs.utils import make_token

log = logging.getLogger(__name__)

@client.on(events.CallbackQuery(pattern=r"^tos_agree_[1-9]\d{0,19}$"))
async def handle_tos_button(evt: events.CallbackQuery.Event):
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

@client.on(events.CallbackQuery(pattern=r"^(fileinfo|groupinfo)_page_(\d+)$"))
async def handle_list_page(evt: events.CallbackQuery.Event) -> None:
    kind = evt.pattern_match.group(1).decode()
    page_no = int(evt.pattern_match.group(2))
    is_group = kind == "groupinfo"

    user_id = evt.sender_id
    label = "group" if is_group else "file"

    total_items = await DB.db.total_files(user_id, is_group=True if is_group else None)
    if total_items == 0:
        await evt.edit(f"You have not generated any {label} links yet.")
        return

    limit = Config.FILE_INDEX_LIMIT
    total_pages = (total_items + limit - 1) // limit

    if page_no < 0 or page_no >= total_pages:
        await evt.answer("Invalid page.", alert=True)
        return

    offset = page_no * limit
    items_gen = (
        DB.db.get_groups(user_id, offset, limit)
        if is_group
        else DB.db.get_files(user_id, offset, limit)
    )

    buttons: list[list[Button]] = []

    async for item_id, name in items_gen:
        buttons.append([
            Button.inline(name, data=f"{label}info_file_{item_id}_{page_no}")
        ])

    if not buttons:
        await evt.edit(f"No {label}s on this page.")
        return

    nav = []
    if page_no > 0:
        nav.append(Button.inline("<<", f"{kind}_page_{page_no - 1}"))

    nav.append(Button.inline(f"Page {page_no + 1}/{total_pages}", b"noop"))

    if page_no + 1 < total_pages:
        nav.append(Button.inline(">>", f"{kind}_page_{page_no + 1}"))

    buttons.append(nav)

    await evt.edit(
        f"You have **{total_items}** {label}s:",
        buttons=buttons
    )

@client.on(events.CallbackQuery(pattern=r"^fileinfo_file_(\d+)_(\d+)$"))
async def handle_fileinfo_button(evt: events.CallbackQuery.Event):
    file_id = int(evt.pattern_match.group(1))
    page_no = int(evt.pattern_match.group(2))
    user_id = evt.sender_id
    file_info = await DB.db.get_file(file_id, user_id)
    if file_info is None:
        await evt.answer("File not found.")
        return
    token = make_token(user_id, file_info.id)
    url = f"{Config.PUBLIC_URL}/dl/{token}"
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
            [Button.url(file_info.file_name, url)],
            [Button.inline("Back", f"fileinfo_page_{page_no}")]
        ]
    )

@client.on(events.CallbackQuery(pattern=r"^groupinfo_file_(\d+)_(\d+)$"))
async def handle_groupinfo_button(evt: events.CallbackQuery.Event):
    file_id = int(evt.pattern_match.group(1))
    page_no = int(evt.pattern_match.group(2))
    user_id = evt.sender_id
    file_info = await DB.db.get_group(file_id, user_id)
    if file_info is None:
        await evt.answer("Group not found.")
        return
    token = make_token(user_id, file_info.group_id)
    buttons: List[List[Button]] = [
        [Button.url("Open", f"{Config.PUBLIC_URL}/group/{token}")]
    ]
    if file_info.files and len(file_info.files) <= 98:
        for file_id in file_info.files:
            buttons.append([Button.inline(str(file_id), f"fileinfo_file_{file_id}_0")])
    buttons.append([Button.inline("Back", f"groupinfo_page_{page_no}")])
    await evt.edit(
        f"Group Info:\n"
        f"Name: {file_info.name}\n"
        f"created_at: {file_info.created_at}\n"
        f"Total Files: {len(file_info.files) if file_info.files else 0}",
        buttons=buttons
    )
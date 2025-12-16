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
from typing import Tuple, cast

from telethon import events, Button
from telethon.custom import Message
from telethon.utils import get_input_location

from tgfs.config import Config
from tgfs.telegram import client, multi_clients
from tgfs.database import DB
from tgfs.types import FileInfo, InputTypeLocation, Status
from tgfs.utils import check_get_user

log = logging.getLogger(__name__)

@client.on(events.NewMessage(incoming=True, pattern=r"^\/start", func=lambda x: x.is_private and not x.file))
async def handle_start_command(evt: events.NewMessage.Event) -> None:
    await evt.reply("Send me any telegram file or photo I will generate a link for it\n\nUse /help to see available commands.")

@client.on(events.NewMessage(incoming=True, pattern=r"^\/help", func=lambda x: x.is_private and not x.file))
async def handle_start_command(evt: events.NewMessage.Event) -> None:
    await evt.reply("""
Available Commands:
/start - Start the bot
/help - Show this help message
/group - Start creating a group of files
/done - Finish adding files to the group
/myfiles - List your uploaded files
/mygroups - List your created groups
""")

@client.on(events.NewMessage(incoming=True, func=lambda x: x.is_private and x.file))
async def handle_file_message(evt: events.NewMessage.Event, msg=None) -> None:
    msg: Message = evt.message if not msg else msg
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    if user.curt_op in [Status.GROUP_NAME, Status.GROUP]:
        return
    dc_id, location = cast(Tuple[int, InputTypeLocation], get_input_location(msg.media))
    file_info = FileInfo(
        id=location.id,
        dc_id=dc_id,
        file_size=msg.file.size,
        mime_type=msg.file.mime_type,
        file_name=msg.file.name or f"{location.id}{msg.file.ext or ''}",
        thumb_size=location.thumb_size,
        is_deleted=False
    )
    await DB.db.add_file(file_info)
    await DB.db.upsert_location(
        multi_clients[0].client_id,
        location
    )
    await DB.db.link_user_file(
        file_info.id,msg.sender_id, msg.id, msg.chat_id
    )
    # fwd_msg: Message = await msg.forward_to(Config.BIN_CHANNEL)
    url = f"{Config.PUBLIC_URL}/dl/{msg.sender_id}/{file_info.id}"
    await evt.reply(url)
    log.info("Generated Link %s", url)

@client.on(events.NewMessage(incoming=True, pattern=r"^\/group", func=lambda x: x.is_private and not x.file))
async def handle_group_command(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    if user.curt_op == Status.NO_OP:
        user.curt_op = Status.GROUP
        user.op_id = msg.id
        await DB.db.upsert_user(user)
        await evt.reply("Send files to add to the group. When done, send /done")
    else:
        await evt.reply("You are already in an operation. Please complete it before starting a new one.")

@client.on(events.NewMessage(incoming=True, pattern=r"^\/done", func=lambda x: x.is_private and not x.file))
async def handle_done_command(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    if user.curt_op == Status.NO_OP:
        await evt.reply("You are not in any operation.")
    elif user.curt_op == Status.GROUP:
        min_id = user.op_id+1
        max_id = msg.id
        order=0
        group_id = await DB.db.create_group(user.user_id, msg.id)
        file_msgs = await client.get_messages(
            entity=msg.chat_id,
            ids=range(min_id, max_id),
        )
        for file_msg in file_msgs:
            if not file_msg.file:
                continue
            dc_id, location = cast(Tuple[int, InputTypeLocation], get_input_location(file_msg.media))
            file_info = FileInfo(
                id=location.id,
                dc_id=dc_id,
                file_size=file_msg.file.size,
                mime_type=file_msg.file.mime_type,
                file_name=file_msg.file.name or f"{location.id}{file_msg.file.ext or ''}",
                thumb_size=location.thumb_size,
                is_deleted=False
            )
            await DB.db.add_file(file_info)
            await DB.db.upsert_location(
                multi_clients[0].client_id,
                location
            )
            order+=1
            await DB.db.link_file_group(group_id, file_info.id, order)
        if order == 0:
            await DB.db.delete_group(group_id, user.user_id)
            await evt.reply("No files were added to the group. Operation cancelled.")
            user.curt_op = Status.NO_OP
            user.op_id = 0
            await DB.db.upsert_user(user)
            return
        await evt.reply("Send a name for your group of files")
        user.curt_op = Status.GROUP_NAME
        user.op_id = group_id
        await DB.db.upsert_user(user)
    else:
        await evt.reply("Unknown operation state.")

@client.on(events.NewMessage(incoming=True, pattern=r"^(?!/).*", func=lambda x: x.is_private and not x.file))
async def handle_text_message(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    if user.curt_op == Status.GROUP_NAME:
        group_id = user.op_id
        name = msg.text.strip()
        await DB.db.set_group_name(group_id, user.user_id, name)
        user.curt_op = Status.NO_OP
        user.op_id = 0
        await DB.db.upsert_user(user)
        url = f"{Config.PUBLIC_URL}/group/{msg.sender_id}/{group_id}"
        await evt.reply(f"Group '{name}' created!\n{url}")
    else:
        await evt.reply("Unknown command")

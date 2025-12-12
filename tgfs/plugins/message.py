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

from telethon import events
from telethon.custom import Message
from telethon import Button

from tgfs.config import Config
from tgfs.telegram import client, multi_clients
from tgfs.database import DB
from tgfs.types import FileInfo, InputMedia, Status

log = logging.getLogger(__name__)

async def check_get_user(user_id: int, msg_id):
    user = await DB.db.get_user(user_id)
    if user is None:
        await client.send_message(
            user_id, "Please agree to the Terms of Service before using the bot.",
            buttons=[[Button.inline('Agree', f'tos_agree_{msg_id}'.encode('utf-8'))]]
        )
    if user is not None and user.is_banned:
        await client.send_message(user_id, "You are banned from using this bot.")
        return None
    return user


@client.on(events.NewMessage(incoming=True, pattern=r"^\/start", func=lambda x: x.is_private and not x.file))
async def handle_text_message(evt: events.NewMessage.Event) -> None:
    await evt.reply("Send me any telegram file or photo I will generate a link for it")

@client.on(events.NewMessage(incoming=True, func=lambda x: x.is_private and x.file))
async def handle_file_message(evt: events.NewMessage.Event, msg=None) -> None:
    msg: Message = evt.message if not msg else msg
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    media: InputMedia = getattr(msg.media, "document", None) or getattr(msg.media, "photo", None)
    file_info = FileInfo(
        id=media.id,
        dc_id=media.dc_id,
        file_size=msg.file.size,
        mime_type=msg.file.mime_type,
        file_name=msg.file.name or f"{media.id}{msg.file.ext or ''}",
        thumb_size="",
        is_deleted=False
    )
    await DB.db.add_file(file_info)
    await DB.db.add_location(
        file_info.id,
        multi_clients[0].client_id,
        media.access_hash,
        media.file_reference
    )
    if user.curt_op == Status.GROUP and user.op_id != 0:
        await DB.db.link_file_group(user.op_id, file_info.id)
        await evt.reply(f"Added to group. Send more files or /done to finish.")
        return
    await DB.db.link_user_file(
        file_info.id,msg.sender_id, msg.id, msg.chat_id
    )
    # fwd_msg: Message = await msg.forward_to(Config.BIN_CHANNEL)
    url = f"{Config.PUBLIC_URL}/dl/{msg.sender_id}/{file_info.id}"
    await evt.reply(url)
    log.info("Generated Link %s", url)

@client.on(events.NewMessage(incoming=True, pattern=r"^\/group", func=lambda x: x.is_private and not x.file))
async def handle_text_message(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    if user.curt_op == Status.NO_OP:
        user.curt_op = Status.GROUP
        await DB.db.upsert_user(user)
        await evt.reply("Send me the name for your group of files")
    else:
        await evt.reply("You are already in an operation. Please complete it before starting a new one.")

@client.on(events.NewMessage(incoming=True, pattern=r"^\/done", func=lambda x: x.is_private and not x.file))
async def handle_text_message(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    if user.curt_op == Status.NO_OP:
        await evt.reply("You are not in any operation.")
    elif user.curt_op == Status.GROUP:
        if user.op_id == 0:
            return await evt.reply("You did not send any group name")
        url = f"{Config.PUBLIC_URL}/group/{msg.sender_id}/{user.op_id}"
        user.curt_op = Status.NO_OP
        user.op_id = 0
        await DB.db.upsert_user(user)
        await evt.reply(url)
        log.info("Generated Group Link %s", url)
    else:
        await evt.reply("Unknown operation state.")

@client.on(events.NewMessage(incoming=True, pattern=r"^(?!/).*", func=lambda x: x.is_private and not x.file))
async def handle_text_message(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    if user.curt_op == Status.GROUP and user.op_id == 0:
        name = msg.text.strip()
        group_id = await DB.db.create_group(user.user_id, name)
        user.op_id = group_id
        await DB.db.upsert_user(user)
        await evt.reply(f"Group '{name}' created! Now send me the files to add to this group. When done, send /done.")
    else:
        await evt.reply("Unknown command")
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

import logging
from typing import cast

from telethon import events, Button
from telethon.custom import Message
from telethon.utils import get_input_location
from telethon.errors import ButtonUrlInvalidError

from tgfs.config import Config
from tgfs.database import DB
from tgfs.telegram import client, multi_clients
from tgfs.utils.translation import get_lang
from tgfs.utils.utils import check_get_user, make_token
from tgfs.utils.types import FileInfo, FileSource, InputTypeLocation, Status


log = logging.getLogger(__name__)


@client.on(events.NewMessage(incoming=True, func=lambda x: x.is_private and x.file))
async def handle_file_message(evt: events.NewMessage.Event, msg=None) -> None:
    msg: Message = evt.message if not msg else msg
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    if user.curt_op in [Status.GROUP_NAME, Status.GROUP]:
        return
    lang = get_lang(user)
    dc_id, location = cast(
        tuple[int, InputTypeLocation], get_input_location(msg.media))
    file_info = FileInfo(
        id=location.id,
        dc_id=dc_id,
        file_size=msg.file.size,
        mime_type=msg.file.mime_type,
        file_name=msg.file.name or f"{location.id}{msg.file.ext or ''}",
        thumb_size=location.thumb_size,
        is_deleted=False
    )
    file_source = FileSource(
        chat_id=msg.chat_id,
        message_id=msg.id,
    )
    await DB.db.add_file(user.user_id, file_info, file_source)
    await DB.db.upsert_location(
        multi_clients[0].client_id,
        location
    )
    # fwd_msg: Message = await msg.forward_to(Config.BIN_CHANNEL)
    token = make_token(msg.sender_id, file_info.id)
    url = f"{Config.PUBLIC_URL}/dl/{token}"
    wt_url = f"{Config.PUBLIC_URL}/wt/{token}"
    try:
        await evt.reply(
            url,
            buttons=[
                [
                    Button.url(lang.DOWNLOAD, url),
                    Button.url(lang.WATCH, wt_url)
                ],
            ]
        )
    except ButtonUrlInvalidError as e:
        log.error("Failed to send download link: %s", e)
        await evt.reply(url)
    log.info("Generated Link %s", url)


@client.on(events.NewMessage(incoming=True, pattern=r"^/group", func=lambda x: x.is_private and not x.file))
async def handle_group_command(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    lang = get_lang(user)
    if user.curt_op == Status.NO_OP:
        user.curt_op = Status.GROUP
        user.op_id = msg.id
        await DB.db.upsert_user(user)
        await evt.reply(lang.GROUP_SENDFILE_TEXT)
    else:
        await evt.reply(lang.ALREADY_IN_OP)


@client.on(events.NewMessage(incoming=True, pattern=r"^/done", func=lambda x: x.is_private and not x.file))
async def handle_done_command(evt: events.NewMessage.Event, user=None) -> None:
    msg: Message = evt.message
    user = user or await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    lang = get_lang(user)
    if user.curt_op == Status.NO_OP:
        await evt.reply(lang.NOT_IN_OP)
    elif user.curt_op == Status.GROUP:
        min_id = user.op_id+1
        max_id = msg.id
        order = 0
        group_id = await DB.db.create_group(user.user_id, str(msg.id))
        try:
            file_msgs: list[Message] = await client.get_messages(
                entity=msg.chat_id,
                ids=range(min_id, max_id),
            )
            for m in file_msgs:
                print(m)
            file_msgs = list(filter(lambda m: m and m.file, file_msgs))
            if not file_msgs:
                await DB.db.delete_group(group_id, user.user_id)
                await evt.reply(lang.GROUP_NOFILES_TEXT)
                user.curt_op = Status.NO_OP
                user.op_id = 0
                await DB.db.upsert_user(user)
                return
            for file_msg in file_msgs:
                dc_id, location = cast(
                    tuple[int, InputTypeLocation], get_input_location(file_msg.media))
                file_info = FileInfo(
                    id=location.id,
                    dc_id=dc_id,
                    file_size=file_msg.file.size,
                    mime_type=file_msg.file.mime_type,
                    file_name=file_msg.file.name or f"{location.id}{file_msg.file.ext or ''}",
                    thumb_size=location.thumb_size,
                    is_deleted=False
                )
                file_source = FileSource(
                    chat_id=file_msg.chat_id,
                    message_id=file_msg.id
                )
                await DB.db.add_file(user.user_id, file_info, file_source)
                await DB.db.upsert_location(
                    multi_clients[0].client_id,
                    location
                )
                order += 1
                await DB.db.add_file_to_group(group_id, user.user_id, file_info.id, order)
            await evt.reply(lang.GROUP_NAME_TEXT)
            user.curt_op = Status.GROUP_NAME
            user.op_id = group_id
            await DB.db.upsert_user(user)
        except Exception as e:
            DB.db.delete_group(group_id, user.user_id)
            log.error(e, exc_info=True, stack_info=True)
    else:
        await evt.reply(lang.UNKNOWN_COMMAND)

@client.on(events.NewMessage(incoming=True, pattern=r"^/files", func=lambda x: x.is_private and not x.file))
async def handle_myfiles_command(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    lang = get_lang(user)
    total_files = await DB.db.total_files(user.user_id)
    total_groups = await DB.db.total_groups(user.user_id)
    await evt.reply(lang.FILES_TEXT.format(total_files=total_files, total_groups=total_groups),
                    buttons=[
        [Button.inline(lang.FILES, "fileinfo_page_0")],
        [Button.inline(lang.GROUPS, "groupinfo_page_0")]
    ]
    )

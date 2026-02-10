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

from telethon import events
from telethon.custom import Message

from tgfs.config import Config
from tgfs.plugins.custom import HANDLERS
from tgfs.telegram import client
from tgfs.database import DB
from tgfs.utils.translation import get_lang, registry
from tgfs.utils.types import Status, User
from tgfs.utils.utils import check_get_user, make_token

log = logging.getLogger(__name__)


@client.on(events.NewMessage(incoming=True, pattern=r"^/start", func=lambda x: x.is_private and not x.file))
async def handle_start_command(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if not user: return
    lang = get_lang(user)
    await evt.reply(lang.START_TEXT)

@client.on(events.NewMessage(incoming=True, pattern=r"^/help", func=lambda x: x.is_private and not x.file))
async def handle_help_command(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if not user: return
    lang = get_lang(user)
    await evt.reply(lang.HELP_TEXT)

@client.on(events.NewMessage(incoming=True, pattern=r"^(?!/).*", func=lambda x: x.is_private and not x.file))
async def handle_text_message(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    lang = get_lang(user)

    message = msg.message.strip()
    if user.curt_op == Status.GROUP_NAME:
        await handle_group_name(evt, user)
    else:
        for pattern, func in HANDLERS:
            m = pattern.match(message)
            if m:
                await func(evt, user, m)
                return

        await evt.reply(lang.UNKNOWN_COMMAND)

async def handle_group_name(evt: events.NewMessage.Event, user: User) -> None:
    lang = get_lang(user)
    msg: Message = evt.message
    name = msg.text.strip()
    group_id = user.op_id
    await DB.db.update_group_name(group_id, user.user_id, name)
    user.curt_op = Status.NO_OP
    user.op_id = 0
    await DB.db.upsert_user(user)
    token = make_token(user.user_id, group_id)
    url = f"{Config.PUBLIC_URL}/group/{token}"
    await evt.reply(lang.GROUP_CREATED_TEXT.format(name=name, url=url))

@client.on(events.NewMessage(incoming=True, pattern=r"^/setln(?:\s+([a-z]{2}))?$", func=lambda x: x.is_private and not x.file))
async def handle_setln_command(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    lang = get_lang(user)
    ln_code = evt.pattern_match.group(1)
    if ln_code is None or ln_code not in registry:
        await evt.reply(lang.SETLN_USAGE_TEXT.format(supported_codes=", ".join(registry.keys())))
        return
    user.preferred_lang = ln_code
    if await DB.db.upsert_user(user):
        await evt.reply(lang.SETLN_SET_TO.format(ln_code=ln_code))
    else:
        await evt.reply(lang.SOMETHING_WENT_WRONG)

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

import datetime
import logging
from typing import Optional

from telethon import events

from tgfs.config import Config
from tgfs.telegram import client
from tgfs.database import DB
from tgfs.utils.utils import parse_token


def is_admin(user_id: int):
    return user_id in Config.ADMIN_IDS


def parse_userid(token: str) -> Optional[int]:
    if token.isdigit():
        return int(token)
    else:
        data = parse_token(token)
        if data:
            return data[0]


log = logging.getLogger(__name__)


@client.on(events.NewMessage(
    incoming=True,
    pattern=r"^/help",
    func=lambda x: x.is_private and not x.file and is_admin(x.sender_id)
))
async def handle_help_command(evt: events.NewMessage.Event) -> None:
    await evt.reply(f"""
Admin Commands:
/ban <userid> <reason>: ban a user
/warn <userid> <reason>: warn a user; after {Config.MAX_WARNS} warnings, the user will be banned
/unban <userid>: unban a user
/clearwarns <userid>: clear all warnings for a user

/listfiles <fileid | token>: list users who generated a link for a specific file
/restrictfile <fileid | token>: restrict a file link to prevent users from downloading the file
/deletefile <userid> <fileid>: delete a file associated with a user
/deletefile <token>: delete a file using its token
/parsetoken <token>: parse a token to retrieve the file ID and user ID

download url strcture: "http://<PUBLIC_URL>/dl/<token>/<signature>"
""")


@client.on(events.NewMessage(
    incoming=True,
    pattern=r"^/ban (\d+) (.+)$",
    func=lambda x: x.is_private and not x.file and is_admin(x.sender_id)
))
async def handle_ban_command(evt: events.NewMessage.Event) -> None:
    user_id = int(evt.pattern_match.group(1))
    reason = str(evt.pattern_match.group(2))
    user = await DB.db.get_user(user_id)
    if not user:
        return await evt.reply("User doesn't exist in Database")
    user.ban_date = datetime.datetime.now(datetime.UTC)
    if await DB.db.upsert_user(user):
        await evt.reply(f"Banned user {user_id}")
        await client.send_message(user_id, f"Your banned\nReason: {reason}")
    else:
        await evt.reply(f"Unable to ban user {user_id}")


@client.on(events.NewMessage(
    incoming=True,
    pattern=r"^/warn (\d+) (.+)$",
    func=lambda x: x.is_private and not x.file and is_admin(x.sender_id)
))
async def handle_warn_command(evt: events.NewMessage.Event) -> None:
    user_id = int(evt.pattern_match.group(1))
    reason = str(evt.pattern_match.group(2))
    user = await DB.db.get_user(user_id)
    if not user:
        return await evt.reply("User doesn't exist in Database")
    user.warns += 1
    if user.warns >= Config.MAX_WARNS:
        await evt.reply("User reached max warns")
        user.ban_date = datetime.datetime.now(datetime.UTC)
    if await DB.db.upsert_user(user):
        await evt.reply(f"User has {user.warns}/{Config.MAX_WARNS} Warns")
        await client.send_message(user_id, f"You have {user.warns}/{Config.MAX_WARNS} Warns\nReason: {reason}")
    else:
        await evt.reply(f"Unable to warn user {user_id}")


@client.on(events.NewMessage(
    incoming=True,
    pattern=r"^/unban (\d+)$",
    func=lambda x: x.is_private and not x.file and is_admin(x.sender_id)
))
async def handle_unban_command(evt: events.NewMessage.Event) -> None:
    user_id = int(evt.pattern_match.group(1))
    user = await DB.db.get_user(user_id)
    if not user:
        return await evt.reply("User doesn't exist in Database")
    user.ban_date = None
    user.warns = 0
    if await DB.db.upsert_user(user):
        await evt.reply("User has Unbanned and Warns reset to 0")
        await client.send_message(user_id, "You are unbanned now you can use this bot")
    else:
        await evt.reply(f"Unable to unban user {user_id}")


@client.on(events.NewMessage(
    incoming=True,
    pattern=r"^/clearwarns (\d+)$",
    func=lambda x: x.is_private and not x.file and is_admin(x.sender_id)
))
async def handle_clearwarns_command(evt: events.NewMessage.Event) -> None:
    user_id = int(evt.pattern_match.group(1))
    user = await DB.db.get_user(user_id)
    if not user:
        return await evt.reply("User doesn't exist in Database")
    user.warns = 0
    if await DB.db.upsert_user(user):
        await evt.reply("Warns reset to 0")
        await client.send_message(user_id, "Your warns reset to 0")
    else:
        await evt.reply(f"Unable to clear warns for user {user_id}")


@client.on(events.NewMessage(
    incoming=True,
    pattern=r"^/listfiles (\d+|[A-Za-z0-9_\-:/]+)$",
    func=lambda x: x.is_private and not x.file and is_admin(x.sender_id)
))
async def handle_listfiles_command(evt: events.NewMessage.Event) -> None:
    file_id = evt.pattern_match.group(1)
    if file_id.isdigit():
        file_id = int(file_id)
    else:
        data = parse_token(file_id)
        if not data:
            return await evt.reply("Invalid File Id")
        file_id = data[1]
    users = await DB.db.get_file_users(file_id)
    if not users:
        return await evt.reply("No users have generated a link for this file.")
    reply_text = (
        "These users generated a link for this file:\n"
        + "\n".join(f"[{uid}](tg://user?id={uid})" for uid in users)
    )
    await evt.reply(reply_text)


@client.on(events.NewMessage(
    incoming=True,
    pattern=r"^/restrictfile (\d+|[A-Za-z0-9_\-:/]+)$",
    func=lambda x: x.is_private and not x.file and is_admin(x.sender_id)
))
async def handle_restrictfile_command(evt: events.NewMessage.Event) -> None:
    file_id = evt.pattern_match.group(1)
    if file_id.isdigit():
        file_id = int(file_id)
    else:
        data = parse_token(file_id)
        if not data:
            return await evt.reply("Invalid File Id")
        file_id = data[1]
    file = await DB.db.get_file(file_id)
    if not file:
        return await evt.reply("File not found in Database")
    file.is_deleted = True
    await DB.db.update_file_restriction(file.id, file.is_deleted)
    await evt.reply(f"Restricted File with File Id {file.id}")


@client.on(events.NewMessage(
    incoming=True,
    pattern=r"^/deletefile (?:(\d+) (\d+)|([A-Za-z0-9_\-:/]+))$",
    func=lambda x: x.is_private and not x.file and is_admin(x.sender_id)
))
async def handle_deletefile_command(evt: events.NewMessage.Event) -> None:
    user_id = evt.pattern_match.group(1)
    file_id = evt.pattern_match.group(2)
    token = evt.pattern_match.group(3)

    if token:
        data = parse_token(token)
        if not data:
            return
        user_id, file_id = data
    else:
        user_id = int(user_id)
        file_id = int(file_id)
    if await DB.db.remove_file(file_id, user_id):
        await evt.reply(f"Deleted file {file_id} from user [{user_id}](tg://user?id={user_id})")
    else:
        await evt.reply(f"Unable to delete file {file_id} associated with user [{user_id}](tg://user?id={user_id})")


@client.on(events.NewMessage(
    incoming=True,
    pattern=r"^/parsetoken ([A-Za-z0-9_\-:/]+)$",
    func=lambda x: x.is_private and not x.file and is_admin(x.sender_id)
))
async def handle_parsetoken_command(evt: events.NewMessage.Event) -> None:
    token = evt.pattern_match.group(1)
    data = parse_token(token)
    if not data:
        return await evt.reply("Invalid Token")
    user_id, file_id = data
    await evt.reply(f"Token {token} is associated with User ID {user_id} and File ID {file_id}")

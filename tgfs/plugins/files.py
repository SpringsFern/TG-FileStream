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

from telethon import events, Button
from telethon.custom import Message

from tgfs.telegram import client
from tgfs.database import DB
from tgfs.utils import check_get_user

log = logging.getLogger(__name__)

@client.on(events.NewMessage(incoming=True, pattern=r"^/files", func=lambda x: x.is_private and not x.file))
async def handle_myfiles_command(evt: events.NewMessage.Event) -> None:
    msg: Message = evt.message
    user = await check_get_user(msg.sender_id, msg.id)
    if user is None:
        return
    total_files = await DB.db.total_files(user.user_id)
    total_groups = await DB.db.total_groups(user.user_id)
    await evt.reply(
        f"""You have created links for:
• Files: {total_files}
• Groups: {total_groups}

Select the type of links you want to view.
""",
        buttons=[
            [Button.inline("Files", "fileinfo_page_0")],
            [Button.inline("Groups", "groupinfo_page_0")]
        ]
    )

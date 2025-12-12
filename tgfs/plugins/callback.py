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

from tgfs.telegram import client
from tgfs.database import DB
# from tgfs.plugins.message import handle_file_message

log = logging.getLogger(__name__)

@client.on(events.CallbackQuery(pattern=r"^tos_agree_[1-9]\d{0,19}$"))
async def handle_buttons(evt: events.CallbackQuery.Event):
    callback_data = evt.data.decode('utf-8')
    log.debug("Callback data: %s", callback_data)
    msg_id = int(callback_data.split("_")[-1])
    user_id = evt.sender_id
    if not await DB.db.add_user(user_id):
        await evt.answer("Something went wrong")
        return
    # msg = await client.get_messages(user_id, ids=msg_id)
    # await handle_file_message(evt, msg)
    await evt.answer("You have agreed to the Terms of Service.")
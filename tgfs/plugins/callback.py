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

from telethon import Button, events
from telethon.tl.types import InputMediaDocument, InputMediaPhoto

from tgfs.config import Config
from tgfs.telegram import client
from tgfs.database import DB
from tgfs.utils.translation import get_lang
from tgfs.utils.utils import check_get_user, make_token

log = logging.getLogger(__name__)


@client.on(events.CallbackQuery(pattern=r"^tos_agree_[1-9]\d{0,19}$"))
async def handle_tos_button(evt: events.CallbackQuery.Event):
    lang = get_lang()
    callback_data = evt.data.decode('utf-8')
    log.debug("Callback data: %s", callback_data)
    user_id = evt.sender_id
    if not await DB.db.add_user(user_id):
        await evt.answer(lang.SOMETHING_WENT_WRONG)
        return
    # msg = await client.get_messages(user_id, ids=msg_id)
    # await handle_file_message(evt, msg)
    await evt.answer(lang.ACCEPTED_TOS_TEXT)
    await evt.edit(buttons=[[Button.inline(lang.AGREED, b"tos_agreed")]])


@client.on(events.CallbackQuery(pattern=r"^(fileinfo|groupinfo)_page_(\d+)$"))
async def handle_list_page(evt: events.CallbackQuery.Event) -> None:
    user = await check_get_user(evt.sender_id, evt.message_id)
    lang = get_lang(user)
    kind = evt.pattern_match.group(1).decode()
    page_no = int(evt.pattern_match.group(2))
    is_group = kind == "groupinfo"

    user_id = evt.sender_id
    label = "group" if is_group else "file"

    total_items = (await DB.db.total_groups(user_id)
                   if is_group else await DB.db.total_files(user_id))
    if total_items == 0:
        await evt.edit(lang.NO_LABEL_LINKS_TEXT.format(label=label))
        return

    limit = Config.FILE_INDEX_LIMIT
    total_pages = (total_items + limit - 1) // limit

    if page_no < 0 or page_no >= total_pages:
        await evt.answer(lang.INVALID_PAGE, alert=True)
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
        await evt.edit(lang.NO_LABELS_TEXT.format(label=label))
        return

    nav = []
    if page_no > 0:
        nav.append(Button.inline("<<", f"{kind}_page_{page_no - 1}"))

    nav.append(Button.inline(
        lang.FILES_BUTTON_CURRENT.format(
            page_no=page_no + 1, total_pages=total_pages),
        b"noop"
    ))

    if page_no + 1 < total_pages:
        nav.append(Button.inline(">>", f"{kind}_page_{page_no + 1}"))

    buttons.append(nav)
    buttons.append([Button.inline(lang.BACK_TEXT, b"files_menu")])

    await evt.edit(
        lang.TOTAL_LABEL_COUNT.format(total=total_items, label=label),
        buttons=buttons
    )


@client.on(events.CallbackQuery(pattern=r"^fileinfo_file_(\d+)_(\d+)$"))
async def handle_fileinfo_button(evt: events.CallbackQuery.Event):
    user = await check_get_user(evt.sender_id, evt.message_id)
    lang = get_lang(user)
    file_id = int(evt.pattern_match.group(1))
    page_no = int(evt.pattern_match.group(2))
    user_id = evt.sender_id
    file_info = await DB.db.get_file(file_id, user_id)
    if file_info is None:
        await evt.answer(lang.FILE_NOT_FOUND_TEXT, alert=True)
        return
    token = make_token(user_id, file_info.id)
    url = f"{Config.PUBLIC_URL}/dl/{token}"
    await evt.edit(
        lang.FILE_INFO_TEXT.format(
            file_id=file_info.id,
            dc_id=file_info.dc_id,
            file_size=file_info.file_size,
            mime_type=file_info.mime_type,
            file_name=file_info.file_name,
            file_type=lang.PHOTO if file_info.thumb_size else lang.DOCUMENT,
            restricted=lang.YES if file_info.is_deleted else lang.NO
        ),
        buttons=[
            [Button.url(lang.EXTERNAL_LINK, url)],
            [
                Button.inline(
                    lang.DELETE, f"fileinfo_delconf2_{file_info.id}_{page_no}"),
                Button.inline(lang.GET_FILE_TEXT,
                              f"fileinfo_get_{file_info.id}")
            ],
            [Button.inline(lang.BACK_TEXT, f"fileinfo_page_{page_no}")]
        ]
    )


@client.on(events.CallbackQuery(pattern=r"^groupinfo_file_(\d+)_(\d+)$"))
async def handle_groupinfo_button(evt: events.CallbackQuery.Event):
    user = await check_get_user(evt.sender_id, evt.message_id)
    lang = get_lang(user)
    file_id = int(evt.pattern_match.group(1))
    page_no = int(evt.pattern_match.group(2))
    user_id = evt.sender_id
    file_info = await DB.db.get_group(file_id, user_id)
    if file_info is None:
        await evt.answer(lang.GROUP_NOT_FOUND_TEXT, alert=True)
        return
    token = make_token(user_id, file_info.group_id)
    buttons: list[list[Button]] = [
        [Button.url(lang.EXTERNAL_LINK, f"{Config.PUBLIC_URL}/group/{token}")]
    ]
    if file_info.files and len(file_info.files) <= 98:
        for file_id in file_info.files:
            buttons.append(
                [Button.inline(str(file_id), f"fileinfo_file_{file_id}_0")])
    buttons.append(
        [Button.inline(lang.BACK_TEXT, f"groupinfo_page_{page_no}")])
    await evt.edit(
        lang.GROUP_INFO_TEXT.format(
            name=file_info.name,
            created_at=file_info.created_at,
            total_files=len(file_info.files) if file_info.files else 0
        ),
        buttons=buttons
    )


@client.on(events.CallbackQuery(pattern=r"^fileinfo_get_(\d+)$"))
async def handle_fileinfo_get_button(evt: events.CallbackQuery.Event):
    user = await check_get_user(evt.sender_id, evt.message_id)
    lang = get_lang(user)
    file_id = int(evt.pattern_match.group(1))
    user_id = evt.sender_id
    file_info = await DB.db.get_file(file_id, user_id)
    if file_info is None:
        await evt.answer(lang.FILE_NOT_FOUND_TEXT, alert=True)
        return
    location = await DB.db.get_location(file_info, Config.BOT_ID)
    input_media = InputMediaPhoto(
        location) if location.thumb_size else InputMediaDocument(location)
    await client.send_file(user_id, input_media, caption=file_info.file_name)


@client.on(events.CallbackQuery(pattern=r"^fileinfo_delconf2_(\d+)_(\d+)$"))
async def handle_fileinfo_del_conf_button(evt: events.CallbackQuery.Event):
    user = await check_get_user(evt.sender_id, evt.message_id)
    lang = get_lang(user)
    file_id = int(evt.pattern_match.group(1))
    page_no = int(evt.pattern_match.group(2))
    user_id = evt.sender_id
    file_info = await DB.db.get_file(file_id, user_id)
    if file_info is None:
        await evt.answer(lang.FILE_NOT_FOUND_TEXT, alert=True)
        return
    await evt.edit(
        lang.CONFIRM_DELETE_TEXT,
        buttons=[
            [Button.inline(lang.YES+' '+lang.DELETE,
                           f"fileinfo_delete_{file_id}_{page_no}")],
            [Button.inline(lang.NO, f"fileinfo_file_{file_id}_{page_no}")]
        ]
    )


@client.on(events.CallbackQuery(pattern=r"^fileinfo_delete_(\d+)_(\d+)$"))
async def handle_fileinfo_del_button(evt: events.CallbackQuery.Event):
    user = await check_get_user(evt.sender_id, evt.message_id)
    lang = get_lang(user)
    file_id = int(evt.pattern_match.group(1))
    page_no = int(evt.pattern_match.group(2))
    user_id = evt.sender_id
    file_info = await DB.db.get_file(file_id, user_id)
    if file_info is None:
        await evt.answer(lang.FILE_NOT_FOUND_TEXT, alert=True)
        return
    await DB.db.remove_file(file_id, user_id)
    await evt.edit(lang.FILE_DELETED_SUCCESSFULLY, buttons=[
        [Button.inline(lang.BACK_TEXT, f"fileinfo_page_{page_no}")]
    ])


@client.on(events.CallbackQuery(pattern=r"^files_menu$"))
async def handle_files_menu_button(evt: events.CallbackQuery.Event):
    user = await check_get_user(evt.sender_id, evt.message_id)
    lang = get_lang(user)
    await evt.edit(
        lang.SELECT_TYPE_OF_FILE,
        buttons=[
            [Button.inline(lang.FILES, "fileinfo_page_0")],
            [Button.inline(lang.GROUPS, "groupinfo_page_0")]
        ]
    )
